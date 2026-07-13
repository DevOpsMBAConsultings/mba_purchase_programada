from odoo import models, fields


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    display_in_product_list = fields.Boolean(
        string="Display in Product List",
        default=False,
        help="If checked, this pricelist prices will be shown as columns in product list view",
    )

    def write(self, vals):
        res = super().write(vals)
        if 'display_in_product_list' in vals:
            # Clear views cache so the columns update immediately in Odoo
            self.env['ir.ui.view'].clear_caches()
        return res

