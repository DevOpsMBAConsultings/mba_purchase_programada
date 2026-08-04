# -*- coding: utf-8 -*-
from odoo import models, fields


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
