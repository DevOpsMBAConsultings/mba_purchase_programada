# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('price_subtotal')
    def _onchange_price_subtotal_adjust_unit_price(self):
        """
        When editing price_subtotal on Purchase Order lines,
        recalculate price_unit inversely based on product_qty and discount.
        """
        for line in self:
            if line.product_qty and line.price_subtotal is not False:
                discount_val = getattr(line, 'discount', 0.0) or 0.0
                discount_factor = 1.0 - (discount_val / 100.0)
                if discount_factor:
                    new_unit_price = line.price_subtotal / (line.product_qty * discount_factor)
                    if abs((line.price_unit or 0.0) - new_unit_price) > 1e-6:
                        line.price_unit = new_unit_price
