# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('price_subtotal')
    def _onchange_price_subtotal_adjust_unit_price(self):
        """
        When editing price_subtotal on Vendor Bills (in_invoice, in_refund),
        recalculate price_unit inversely based on quantity and discount.
        """
        for line in self:
            if not line.move_id or line.move_id.move_type not in ('in_invoice', 'in_refund'):
                continue
            if line.quantity and line.price_subtotal is not False:
                discount_factor = 1.0 - ((line.discount or 0.0) / 100.0)
                if discount_factor:
                    new_unit_price = line.price_subtotal / (line.quantity * discount_factor)
                    if abs((line.price_unit or 0.0) - new_unit_price) > 1e-6:
                        line.price_unit = new_unit_price
