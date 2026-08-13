# -*- coding: utf-8 -*-

from datetime import date
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mba_sales_history_ids = fields.One2many(
        'mba.product.sales.history',
        'product_tmpl_id',
        string='Historial de Ventas',
    )

    # Rolling window: M-1 = mes más reciente, M-4 = más antiguo
    mba_sold_m1 = fields.Float(
        'M-1', compute='_compute_mba_sales_history',
        digits=(16, 0), store=True, readonly=True,
    )
    mba_sold_m2 = fields.Float(
        'M-2', compute='_compute_mba_sales_history',
        digits=(16, 0), store=True, readonly=True,
    )
    mba_sold_m3 = fields.Float(
        'M-3', compute='_compute_mba_sales_history',
        digits=(16, 0), store=True, readonly=True,
    )
    mba_sold_m4 = fields.Float(
        'M-4', compute='_compute_mba_sales_history',
        digits=(16, 0), store=True, readonly=True,
    )
    mba_sold_total_4m = fields.Float(
        'Total 4M', compute='_compute_mba_sales_history',
        digits=(16, 0), store=True, readonly=True,
    )

    # Etiquetas con nombre real del mes (ej. "Jul 2026")
    mba_label_m1 = fields.Char(
        'Etiqueta M-1', compute='_compute_mba_sales_history',
        store=True, readonly=True,
    )
    mba_label_m2 = fields.Char(
        'Etiqueta M-2', compute='_compute_mba_sales_history',
        store=True, readonly=True,
    )
    mba_label_m3 = fields.Char(
        'Etiqueta M-3', compute='_compute_mba_sales_history',
        store=True, readonly=True,
    )
    mba_label_m4 = fields.Char(
        'Etiqueta M-4', compute='_compute_mba_sales_history',
        store=True, readonly=True,
    )

    MONTH_NAMES = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic',
    }

    @api.depends(
        'mba_sales_history_ids.units_sold',
        'mba_sales_history_ids.month',
        'mba_sales_history_ids.year',
    )
    def _compute_mba_sales_history(self):
        today = date.today()

        # Construir lista de los últimos 4 meses completos
        # (mes anterior al corriente y 3 más hacia atrás)
        months = []
        for offset in range(1, 5):
            m = today.month - offset
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            months.append((m, y))
        # months[0] = M-1 (más reciente), months[3] = M-4 (más antiguo)

        for tmpl in self:
            history = {
                (h.month, h.year): h.units_sold
                for h in tmpl.mba_sales_history_ids
            }
            vals = [history.get((m, y), 0.0) for m, y in months]

            tmpl.mba_sold_m1 = vals[0]
            tmpl.mba_sold_m2 = vals[1]
            tmpl.mba_sold_m3 = vals[2]
            tmpl.mba_sold_m4 = vals[3]
            tmpl.mba_sold_total_4m = sum(vals)

            tmpl.mba_label_m1 = "{} {}".format(
                self.MONTH_NAMES.get(months[0][0], ''), months[0][1])
            tmpl.mba_label_m2 = "{} {}".format(
                self.MONTH_NAMES.get(months[1][0], ''), months[1][1])
            tmpl.mba_label_m3 = "{} {}".format(
                self.MONTH_NAMES.get(months[2][0], ''), months[2][1])
            tmpl.mba_label_m4 = "{} {}".format(
                self.MONTH_NAMES.get(months[3][0], ''), months[3][1])
