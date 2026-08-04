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
    
    internal_vendor_note = fields.Char(
        string='Vendor',
        help="Internal note for product vendor."
    )

    free_qty_available = fields.Float(
        string='Stock Disp.',
        compute='_compute_free_qty_available',
        digits='Product Unit of Measure',
        help="Cantidad disponible libre en inventario para este producto en el almacén de la cotización."
    )

    @api.depends('product_id', 'order_id.warehouse_id')
    def _compute_free_qty_available(self):
        for line in self:
            if line.product_id:
                product = line.product_id
                if 'warehouse_id' in line.order_id._fields and line.order_id.warehouse_id:
                    product = product.with_context(warehouse=line.order_id.warehouse_id.id)
                line.free_qty_available = getattr(product, 'free_qty', getattr(product, 'qty_available', 0.0))
            else:
                line.free_qty_available = 0.0



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
