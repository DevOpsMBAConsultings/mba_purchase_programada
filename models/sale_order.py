# -*- coding: utf-8 -*-
import base64
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    imported_from_pdf = fields.Boolean(
        string='Importado desde PDF',
        default=False,
        copy=False,
        help='Indica si esta cotización fue generada automáticamente a partir de una importación de documento PDF.',
    )
    origin_customer_name = fields.Char(
        string='Cliente Original (PDF)',
        copy=False,
        help='Nombre de la empresa o cliente extraído originalmente del documento PDF.',
    )
    legacy_quotation_number = fields.Char(
        string='No. Cotización Original',
        copy=False,
        help='Referencia o número de cotización originada en el sistema anterior.',
    )
    has_import_warnings = fields.Boolean(
        string='Tiene Alertas de Importación',
        default=False,
        copy=False,
        help='Activa el banner visual de advertencia cuando la importación requiere homologación o revisión.',
    )
    import_warning_message = fields.Text(
        string='Detalle de Alerta de Importación',
        copy=False,
        help='Descripción detallada de las líneas o cliente que requieren revisión por parte del vendedor.',
    )

    @api.model
    def _create_sale_order_from_quotation_pdf(self, parsed, filename, pdf_bytes, attachment=False):
        """Crea una orden de venta importada desde PDF.
        Importa exclusivamente el cliente y los productos/cantidades/precios,
        permitiendo que Odoo asigne automáticamente los vendedores, términos de pago,
        impuestos y listas de precios configurados nativamente en el sistema.
        """
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

        # 2. Homologación de Vendedor (Salesperson)
        user_id = False
        salesperson = parsed.get('salesperson')
        if salesperson:
            user = self.env['res.users'].search([
                ('name', '=ilike', salesperson.strip()),
                ('company_id', 'in', [self.env.company.id, False]),
            ], limit=1)
            if user:
                user_id = user.id
            else:
                warnings.append(_('• Vendedor extraído del PDF ("%s") no fue encontrado en los usuarios de Odoo.') % salesperson)

        # Si no vino en el PDF o no se encontró, tomar el vendedor asignado a la ficha del cliente
        if not user_id and partner.user_id:
            user_id = partner.user_id.id

        # 3. Homologación de Líneas de Pedido (Cliente y Productos alineados)
        order_lines = []
        for line in parsed.get('lines', []):
            code = line.get('code', '').strip()
            desc = line.get('description', '').strip()
            qty = line.get('qty', 1.0)
            price_unit = line.get('price_unit', 0.0)

            product = False
            if code:
                product = self.env['product.product'].search([
                    '|',
                    ('default_code', '=ilike', code),
                    ('barcode', '=', code),
                ], limit=1)

            if product:
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'price_unit': price_unit,
                }))
            else:
                missing_code_label = code if code else _('SIN CÓDIGO')
                line_desc = _('[%s - NO ENCONTRADO EN CATÁLOGO] %s') % (missing_code_label, desc)
                warnings.append(_('• Producto no encontrado en catálogo: [%s] %s (Cantidad: %s, Precio: %s).') % (missing_code_label, desc, qty, price_unit))

                order_lines.append((0, 0, {
                    'name': line_desc,
                    'product_uom_qty': qty,
                    'price_unit': price_unit,
                }))

        has_warnings = bool(warnings)
        warning_msgs = "\n".join(warnings) if warnings else False

        # Encabezado del pedido: Cliente, Vendedor y datos de auditoría
        order_vals = {
            'partner_id': partner.id,
            'date_order': parsed.get('date_order') or fields.Date.context_today(self),
            'imported_from_pdf': True,
            'origin_customer_name': customer_name if customer_name and partner.name == 'Consumidor Final' else False,
            'legacy_quotation_number': parsed.get('quotation_number', ''),
            'client_order_ref': parsed.get('quotation_number', ''),
            'has_import_warnings': has_warnings,
            'import_warning_message': warning_msgs,
        }
        if user_id:
            order_vals['user_id'] = user_id

        order = self.create(order_vals)

        # Agregar las líneas (Odoo computará automáticamente impuestos y totales nativos)
        if order_lines:
            order.write({'order_line': order_lines})

        # Adjuntar PDF al chatter de la cotización
        if attachment:
            attachment.write({'res_model': 'sale.order', 'res_id': order.id})
            order.message_post(
                body=_("Cotización importada automáticamente desde archivo PDF: %s") % filename,
                attachment_ids=attachment.ids
            )
        else:
            new_att = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(pdf_bytes),
                'res_model': 'sale.order',
                'res_id': order.id,
            })
            order.message_post(
                body=_("Cotización importada desde documento PDF: %s") % filename,
                attachment_ids=new_att.ids
            )

        return order

    @api.model
    def _create_order_from_attachment(self, attachment_ids):
        """Intercepta el botón nativo Subir archivo / arrastrar PDF de Odoo en la vista de Presupuestos
        para procesar automáticamente las cotizaciones PDF en lugar de generar un borrador en blanco."""
        attachments = self.env['ir.attachment'].browse(attachment_ids)
        if not attachments:
            return super()._create_order_from_attachment(attachment_ids)

        orders = self.browse()
        other_attachment_ids = []

        for attachment in attachments:
            filename = attachment.name or ''
            is_pdf = attachment.mimetype == 'application/pdf' or filename.lower().endswith('.pdf')
            pdf_bytes = attachment.raw or (base64.b64decode(attachment.datas) if attachment.datas else False)
            if is_pdf and pdf_bytes:
                try:
                    from ..wizard.pdf_parser import QuotationPDFParser
                    parsed = QuotationPDFParser.parse_pdf_bytes(pdf_bytes, filename=filename)
                    if parsed and (parsed.get('lines') or parsed.get('customer_name') or parsed.get('quotation_number')):
                        order = self._create_sale_order_from_quotation_pdf(
                            parsed=parsed,
                            filename=filename,
                            pdf_bytes=pdf_bytes,
                            attachment=attachment,
                        )
                        orders |= order
                        continue
                except Exception as e:
                    _logger.warning("No se pudo importar automáticamente el PDF como cotización (%s): %s", filename, str(e))
            other_attachment_ids.append(attachment.id)

        if other_attachment_ids:
            orders |= super()._create_order_from_attachment(other_attachment_ids)

        return orders
