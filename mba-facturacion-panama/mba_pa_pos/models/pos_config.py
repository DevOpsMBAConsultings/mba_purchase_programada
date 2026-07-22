# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    l10n_pa_fiscal_printer = fields.Boolean(
        string="Usa Impresora Fiscal",
        default=False,
        help=(
            "Si está activo, las facturas POS se manejan con la impresora fiscal "
            "y NO se envían al PAC (DGI). Si está desactivado, las facturas POS "
            "se generan como account.move en borrador con campos DGI para ser "
            "enviadas al PAC mediante el wizard de confirmación."
        ),
    )

    l10n_pa_dgi_document_type_id = fields.Many2one(
        "dgi.document.type",
        string="Tipo de Documento DGI (POS)",
        help="Tipo de documento fiscal por defecto para las facturas generadas desde este POS.",
    )

    l10n_pa_pos_journal_id = fields.Many2one(
        "account.journal",
        string="Diario DGI (POS)",
        domain=[("type", "=", "sale")],
        help=(
            "Diario contable específico para facturas DGI generadas desde este POS. "
            "Debe tener configurado el Código de Sucursal y Punto de Facturación DGI. "
            "Si se deja vacío, se usa el Diario de Facturas estándar del POS."
        ),
    )
