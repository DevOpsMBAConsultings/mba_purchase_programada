# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MbaProductSalesHistory(models.Model):
    _name = 'mba.product.sales.history'
    _description = 'MBA - Historial de Ventas Mensuales por Producto (MBA Consultings)'
    _rec_name = 'product_tmpl_id'
    _order = 'year desc, month desc'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Producto',
        required=True,
        ondelete='cascade',
        index=True,
    )
    month = fields.Integer('Mes', required=True)   # 1-12
    year = fields.Integer('Año', required=True)    # ej. 2026
    units_sold = fields.Float(
        'Unidades Vendidas',
        digits=(16, 0),
        default=0.0,
    )
    period_label = fields.Char(
        'Periodo',
        compute='_compute_period_label',
        store=True,
    )

    _sql_constraints = [
        (
            'unique_product_period',
            'UNIQUE(product_tmpl_id, month, year)',
            'Ya existe un registro de ventas para este producto en ese mes/año.',
        )
    ]

    MONTH_NAMES = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic',
    }

    @api.depends('month', 'year')
    def _compute_period_label(self):
        for rec in self:
            if rec.month and rec.year:
                month_name = self.MONTH_NAMES.get(rec.month, str(rec.month))
                rec.period_label = f"{month_name} {rec.year}"
            else:
                rec.period_label = False
