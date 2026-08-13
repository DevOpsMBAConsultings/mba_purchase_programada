# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # --- MBA: "A la mano" en el almacén de recepción de esta orden ---
    # No se relaciona con un campo core (purchase.order.line no trae
    # existencia física) ni se guarda (store=True), porque depende del
    # almacén de la orden (picking_type_id.warehouse_id), que puede
    # cambiar mientras la orden sigue en borrador. Se calcula igual que
    # qty_on_hand en stock.warehouse.orderpoint: existencia física por
    # almacén, vía el contexto 'warehouse' que ya soporta qty_available.
    mba_qty_on_hand = fields.Float(
        string='A la mano',
        compute='_compute_mba_qty_on_hand',
        digits='Product Unit of Measure',
        help='Existencia física del producto en el almacén de recepción '
             'de esta orden (Entregar en > Almacén). Si la orden no tiene '
             'almacén definido, o el producto no maneja inventario, se '
             'muestra 0.',
    )

    # --- MBA: Historial de ventas de Sage (rolling window 4 meses) ---
    # Mismo patrón que stock_warehouse_orderpoint.py: related directo a
    # los campos ya calculados en product.template (mb_stock_orderpoint_vendor
    # es dueño único de ese cálculo, ver models/product_template.py).
    mba_sold_m1 = fields.Float(
        related='product_id.product_tmpl_id.mba_sold_m1', store=True, readonly=True)
    mba_sold_m2 = fields.Float(
        related='product_id.product_tmpl_id.mba_sold_m2', store=True, readonly=True)
    mba_sold_m3 = fields.Float(
        related='product_id.product_tmpl_id.mba_sold_m3', store=True, readonly=True)
    mba_sold_m4 = fields.Float(
        related='product_id.product_tmpl_id.mba_sold_m4', store=True, readonly=True)
    mba_sold_total_4m = fields.Float(
        related='product_id.product_tmpl_id.mba_sold_total_4m', store=True, readonly=True)

    @api.depends('product_id', 'order_id.picking_type_id.warehouse_id')
    def _compute_mba_qty_on_hand(self):
        for line in self:
            warehouse = line.order_id.picking_type_id.warehouse_id
            if line.product_id and warehouse:
                line.mba_qty_on_hand = line.product_id.with_context(
                    warehouse=warehouse.id).qty_available
            else:
                line.mba_qty_on_hand = 0.0
