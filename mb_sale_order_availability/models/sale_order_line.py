from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    free_qty_available = fields.Float(
        string='Stock Disp.',
        compute='_compute_free_qty_available',
        digits=(16, 0),
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
