from odoo import api, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.depends('name')
    def _compute_display_name(self):
        super()._compute_display_name()
        if self.env.context.get('show_price_in_pricelist_name'):
            product_id = self.env.context.get('product_id')
            if product_id:
                product = self.env['product.product'].browse(product_id).exists()
                if product:
                    qty = self.env.context.get('product_uom_qty') or 1.0
                    uom_id = self.env.context.get('product_uom')
                    uom = self.env['uom.uom'].browse(uom_id).exists() if uom_id else None
                    date = self.env.context.get('date_order')
                    for pricelist in self:
                        try:
                            price = pricelist._get_product_price(
                                product,
                                quantity=qty,
                                uom=uom,
                                date=date
                            )
                            symbol = pricelist.currency_id.symbol or ''
                            pricelist.display_name = f"{pricelist.name} ({price:,.2f} {symbol})".strip()
                        except Exception:
                            pass

    def name_get(self):
        if self.env.context.get('show_price_in_pricelist_name'):
            product_id = self.env.context.get('product_id')
            if product_id:
                product = self.env['product.product'].browse(product_id).exists()
                if product:
                    qty = self.env.context.get('product_uom_qty') or 1.0
                    uom_id = self.env.context.get('product_uom')
                    uom = self.env['uom.uom'].browse(uom_id).exists() if uom_id else None
                    date = self.env.context.get('date_order')
                    res = []
                    for pricelist in self:
                        try:
                            price = pricelist._get_product_price(
                                product,
                                quantity=qty,
                                uom=uom,
                                date=date
                            )
                            symbol = pricelist.currency_id.symbol or ''
                            name = f"{pricelist.name} ({price:,.2f} {symbol})".strip()
                            res.append((pricelist.id, name))
                        except Exception:
                            res.append((pricelist.id, pricelist.name))
                    return res
        return super().name_get()
