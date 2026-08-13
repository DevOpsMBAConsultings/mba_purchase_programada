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
        return self.env['sale.order']._create_sale_order_from_quotation_pdf(
            parsed=parsed,
            filename=filename,
            pdf_bytes=pdf_bytes,
            attachment=False,
        )
