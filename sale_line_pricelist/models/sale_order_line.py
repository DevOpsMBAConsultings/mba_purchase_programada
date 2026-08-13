from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        compute='_compute_line_pricelist_id',
        store=True,
        readonly=False,
        help="Pricelist applied to this specific line."
    )
    
    internal_vendor_note = fields.Text(
        string='Vendor',
        compute='_compute_internal_vendor_note',
        store=True,
        readonly=False,
        help="Internal note for product vendor. Auto-populated from product's purchase tab."
    )

    @api.depends('product_id.seller_ids.partner_id')
    def _compute_internal_vendor_note(self):
        for line in self:
            if line.product_id and line.product_id.seller_ids:
                vendors = line.product_id.seller_ids.mapped('partner_id.name')
                # Remove duplicates while preserving order
                unique_vendors = list(dict.fromkeys(vendors))
                line.internal_vendor_note = '\n'.join(unique_vendors)
            else:
                line.internal_vendor_note = False

    @api.depends('order_id.pricelist_id')
    def _compute_line_pricelist_id(self):
        for line in self:
            if not line.line_pricelist_id and line.order_id.pricelist_id:
                line.line_pricelist_id = line.order_id.pricelist_id

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'line_pricelist_id', 'order_id.pricelist_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or line.display_type:
                line.pricelist_item_id = False
            else:
                pricelist = line.line_pricelist_id or line.order_id.pricelist_id
                if not pricelist:
                    line.pricelist_item_id = False
                else:
                    line.pricelist_item_id = pricelist._get_product_rule(
                        line.product_id,
                        quantity=line.product_uom_qty or 1.0,
                        uom=line.product_uom,
                        date=line.order_id.date_order or fields.Datetime.now(),
                    )

    @api.onchange('line_pricelist_id')
    def _onchange_line_pricelist_id(self):
        # Trigger price recomputation when the pricelist changes in the UI
        self._compute_price_unit()
