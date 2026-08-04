# -*- coding: utf-8 -*-
import base64
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .pdf_parser import QuotationPDFParser

_logger = logging.getLogger(__name__)


class SaleOrderImportPdfWizard(models.TransientModel):
    _name = 'sale.order.import.pdf.wizard'
    _description = 'Wizard para Importación de Cotizaciones en PDF'

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Archivos PDF de Cotización',
        required=True,
        help='Seleccione uno o varios archivos PDF de cotizaciones para importar masivamente en Odoo.',
    )

    def action_import_pdf(self):
        self.ensure_one()
        if not self.attachment_ids:
            raise UserError(_('Por favor, seleccione al menos un archivo PDF para procesar.'))

        created_orders = self.env['sale.order']

        for attachment in self.attachment_ids:
            pdf_bytes = base64.b64decode(attachment.datas)
            filename = attachment.name or 'cotizacion.pdf'

            try:
                parsed = QuotationPDFParser.parse_pdf_bytes(pdf_bytes, filename=filename)
            except Exception as e:
                _logger.exception('Error al procesar el archivo PDF %s: %s', filename, str(e))
                raise UserError(_('Error procesando el archivo "%s": %s') % (filename, str(e)))

            order = self._create_order_from_parsed_data(parsed, filename, pdf_bytes)
            created_orders |= order

        if len(created_orders) == 1:
            return {
                'name': _('Cotización Importada'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id': created_orders.id,
                'target': 'current',
            }
        else:
            return {
                'name': _('Cotizaciones Importadas (%s)') % len(created_orders),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'list,form',
                'domain': [('id', 'in', created_orders.ids)],
                'target': 'current',
            }

    def _create_order_from_parsed_data(self, parsed, filename, pdf_bytes):
        warnings = []

        # 1. Homologación de Cliente (Partner) -> Si no existe, usar Consumidor Final
        partner = False
        customer_name = parsed.get('customer_name')
        if customer_name:
            partner = self.env['res.partner'].search([
                ('name', '=ilike', customer_name.strip()),
                ('company_id', 'in', [self.env.company.id, False]),
            ], limit=1)

        if not partner:
            # Buscar o crear Consumidor Final
            partner = self.env['res.partner'].search([
                ('name', '=ilike', '%Consumidor Final%'),
                ('company_id', 'in', [self.env.company.id, False]),
            ], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': 'Consumidor Final',
                    'company_type': 'person',
                    'company_id': self.env.company.id,
                })
            orig_name = customer_name or _('Desconocido en PDF')
            warnings.append(_('• Cliente no encontrado en el catálogo: se asignó Consumidor Final (Cliente original en PDF: "%s").') % orig_name)

        # 2. Homologación de Vendedor
        user_id = self.env.user.id
        salesperson = parsed.get('salesperson')
        if salesperson:
            user = self.env['res.users'].search([
                ('name', '=ilike', salesperson.strip()),
                ('company_id', 'in', [self.env.company.id, False]),
            ], limit=1)
            if user:
                user_id = user.id

        # 3. Homologación de Término de Pago
        payment_term_id = False
        payment_term_str = parsed.get('payment_term')
        if payment_term_str:
            term = self.env['account.payment.term'].search([
                ('name', '=ilike', payment_term_str.strip()),
                ('company_id', 'in', [self.env.company.id, False]),
            ], limit=1)
            if term:
                payment_term_id = term.id

        # 4. Homologación de Líneas de Pedido (con Opción 1: producto no encontrado -> sin product_id + warning)
        order_lines = []
        for line in parsed.get('lines', []):
            code = line.get('code', '').strip()
            desc = line.get('description', '').strip()
            qty = line.get('qty', 1.0)
            price_unit = line.get('price_unit', 0.0)
            tax_exempt = line.get('tax_exempt', False)

            product = False
            if code:
                product = self.env['product.product'].search([
                    '|',
                    ('default_code', '=ilike', code),
                    ('barcode', '=', code),
                ], limit=1)

            if product:
                line_desc = product.get_product_multiline_description_sale() or desc
                # Gestión de impuestos del producto o exención según PDF
                taxes = product.taxes_id.filtered(lambda t: t.company_id == self.env.company)
                if tax_exempt:
                    tax_ids = []
                else:
                    tax_ids = taxes.ids
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': line_desc,
                    'product_uom_qty': qty,
                    'price_unit': price_unit,
                    'tax_id': [(6, 0, tax_ids)],
                }))
            else:
                # Opción 1: importamos la línea sin producto y agregamos alerta
                missing_code_label = code if code else _('SIN CÓDIGO')
                line_desc = _('[%s - NO ENCONTRADO EN CATÁLOGO] %s') % (missing_code_label, desc)
                warnings.append(_('• Producto no encontrado en catálogo: [%s] %s (Cantidad: %s, Precio: %s).') % (missing_code_label, desc, qty, price_unit))

                # Determinar impuesto por defecto para línea sin producto
                tax_ids = []
                if not tax_exempt:
                    default_tax = self.env['account.tax'].search([
                        ('company_id', '=', self.env.company.id),
                        ('type_tax_use', '=', 'sale'),
                    ], limit=1)
                    if default_tax:
                        tax_ids = default_tax.ids

                order_lines.append((0, 0, {
                    'product_id': False,
                    'name': line_desc,
                    'product_uom_qty': qty,
                    'price_unit': price_unit,
                    'tax_id': [(6, 0, tax_ids)],
                }))

        has_warnings = len(warnings) > 0
        warning_msg = '\n'.join(warnings) if has_warnings else False

        # 5. Creación del Pedido de Venta (draft)
        order_vals = {
            'partner_id': partner.id,
            'user_id': user_id,
            'date_order': parsed.get('date_order') or fields.Date.context_today(self),
            'imported_from_pdf': True,
            'origin_customer_name': customer_name if customer_name and partner.name == 'Consumidor Final' else False,
            'legacy_quotation_number': parsed.get('quotation_number'),
            'client_order_ref': parsed.get('quotation_number'),
            'has_import_warnings': has_warnings,
            'import_warning_message': warning_msg,
            'order_line': order_lines,
        }
        if payment_term_id:
            order_vals['payment_term_id'] = payment_term_id

        order = self.env['sale.order'].create(order_vals)

        # 6. Adjuntar documento original al Chatter y registrar mensaje
        chatter_body = _('<p><b>Cotización importada automáticamente desde PDF.</b></p>')
        if has_warnings:
            chatter_body += _('<p><b>⚠️ Advertencias de Homologación:</b><br/>%s</p>') % '<br/>'.join(warnings)

        order.message_post(
            body=chatter_body,
            attachments=[(filename, pdf_bytes)],
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        return order
