from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        help="Pricelist applied to this specific line."
    )
    
    internal_vendor_note = fields.Char(
        string='Vendor',
        help="Internal note for product vendor."
    )

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'line_pricelist_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or line.display_type or not line.line_pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.line_pricelist_id._get_product_rule(
                    line.product_id,
                    quantity=line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line._get_order_date(),
                )

    @api.onchange('line_pricelist_id')
    def _onchange_line_pricelist_id(self):
        # Trigger price recomputation when the pricelist changes in the UI
        self._compute_price_unit()
