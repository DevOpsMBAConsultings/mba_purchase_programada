# -*- coding: utf-8 -*-
import base64
import json
import logging
from datetime import datetime
import requests
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HKAImportWizard(models.TransientModel):
    _name = 'hka.import.wizard'
    _description = 'Asistente para Importar Factura desde HKA'

    cufe = fields.Char(string='CUFE', required=True, help="Código Único de Factura Electrónica (66 caracteres)")

    def action_import_invoice(self):
        self.ensure_one()
        company = self.env.company

        # Asegurarse de tener token válido
        company.action_hka_get_token()
        if not company.l10n_pa_hka_token:
            raise UserError(_("No se pudo obtener el token de conexión con HKA."))

        url = f"{company.l10n_pa_hka_url.rstrip('/')}/Descarga"
        headers = {
            'Authorization': f'Bearer {company.l10n_pa_hka_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "cufe": self.cufe.strip(),
            "tipoArchivo": "XML"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                raise UserError(_("Error HTTP %(code)s al contactar con HKA: %(text)s") % {'code': response.status_code, 'text': response.text})
                
            data = response.json()
            if str(data.get("Codigo")) != "0" or not data.get("Archivo"):
                raise UserError(_("Error de HKA: %s") % data.get("Mensaje", "Respuesta inválida"))
                
            xml_base64 = data.get("Archivo")
            xml_content = base64.b64decode(xml_base64)
            
            # Parse XML
            return self._parse_and_create_invoice(xml_content, xml_base64)
            
        except requests.exceptions.RequestException as e:
            raise UserError(_("Error de red al conectar con HKA: %s") % str(e))
        except etree.XMLSyntaxError as e:
            raise UserError(_("El archivo descargado no es un XML válido: %s") % str(e))
        except Exception as e:
            raise UserError(_("Ocurrió un error inesperado durante la importación: %s") % str(e))

    def _parse_and_create_invoice(self, xml_content, xml_base64):
        # Evitar problemas con namespaces en lxml
        root = etree.fromstring(xml_content)
        
        # Función auxiliar para buscar nodos sin importar el namespace
        def get_node_text(node, tag_name, default=""):
            found = node.xpath(f"//*[local-name()='{tag_name}']")
            return found[0].text if found else default

        # 1. Extraer datos del emisor y receptor
        ruc_receptor = get_node_text(root, 'numeroRUC')
        nombre_receptor = get_node_text(root, 'razonSocial')
        
        # Buscar el cliente en Odoo
        partner = self.env['res.partner'].search([('vat', '=', ruc_receptor)], limit=1)
        if not partner:
            # Intentar buscar por l10n_pa_ruc si existe
            if hasattr(self.env['res.partner'], 'l10n_pa_ruc'):
                partner = self.env['res.partner'].search([('l10n_pa_ruc', '=', ruc_receptor)], limit=1)
                
            if not partner:
                # Crear cliente si no existe
                partner = self.env['res.partner'].create({
                    'name': nombre_receptor or f'Cliente {ruc_receptor}',
                    'vat': ruc_receptor,
                    'is_company': True,
                })

        # 2. Extraer fecha
        fecha_emision_str = get_node_text(root, 'fechaEmision')
        invoice_date = False
        if fecha_emision_str:
            try:
                # Formato típico HKA: 2026-08-04T15:30:00-05:00
                date_part = fecha_emision_str.split('T')[0]
                invoice_date = datetime.strptime(date_part, '%Y-%m-%d').date()
            except ValueError:
                pass

        # 3. Extraer totales y líneas
        # Por simplicidad y para cuadrar exactamente los impuestos y centavos, 
        # creamos una sola línea global por el subtotal y aplicamos el ITBMS global, 
        # a menos que requieran detalle por línea.
        # Buscaremos items
        items = root.xpath("//*[local-name()='item']")
        invoice_lines = []
        
        # Buscar el impuesto ITBMS base de compras (7%)
        # Como es importación de factura de CLIENTE (ellos emitieron y nosotros bajamos),
        # usaremos los impuestos de venta.
        tax_7 = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('amount', '=', 7.0),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        for item in items:
            desc = get_node_text(item, 'descripcion', 'Item')
            qty = float(get_node_text(item, 'cantidad', '1.0'))
            price = float(get_node_text(item, 'precioUnitario', '0.0'))
            tasa_itbms = get_node_text(item, 'tasaITBMS', '00')
            
            line_vals = {
                'name': desc,
                'quantity': qty,
                'price_unit': price,
            }
            if tasa_itbms == '01' and tax_7: # 01 es 7% en Panamá
                line_vals['tax_ids'] = [(6, 0, [tax_7.id])]
            
            invoice_lines.append((0, 0, line_vals))

        if not invoice_lines:
            # Fallback a una sola línea si no hay items legibles
            total_neto = float(get_node_text(root, 'totalPrecioNeto', '0.0'))
            invoice_lines.append((0, 0, {
                'name': 'Importación Global Factura',
                'quantity': 1,
                'price_unit': total_neto,
            }))

        # 4. Crear la factura (account.move)
        numero_documento = get_node_text(root, 'numeroDocumentoFiscal', '')
        
        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': invoice_date or fields.Date.context_today(self),
            'invoice_line_ids': invoice_lines,
        }
        
        if numero_documento:
            move_vals['name'] = numero_documento
            
        # Guardar CUFE y estado PAC si el módulo base lo soporta
        if hasattr(self.env['account.move'], 'l10n_pa_cufe'):
            move_vals['l10n_pa_cufe'] = self.cufe
            move_vals['l10n_pa_pac_status'] = 'accepted'
        
        move = self.env['account.move'].create(move_vals)
        
        # 5. Publicar (Bypass de validación local DGI para facturas importadas)
        move.with_context(skip_pac_send=True).action_post()
        
        # 6. Adjuntar XML
        filename = f"{self.cufe}.xml"
        self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': xml_base64,
            'res_model': 'account.move',
            'res_id': move.id,
            'mimetype': 'application/xml',
        })

        # Retornar vista de la factura creada
        return {
            'name': _('Factura Importada'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'target': 'current',
        }
