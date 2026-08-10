# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class PurchaseProgramadaLine(models.TransientModel):
    """Una fila por cada producto que tiene al proveedor de la orden
    configurado en su pestaña "Compras" (product.supplierinfo). Vive
    dentro del formulario de mba.purchase.programada.wizard (campo
    line_ids): se muestran todas, sin necesidad de marcar checkboxes, y
    al confirmar (ver PurchaseProgramadaWizard.action_add_to_order) solo
    se agregan a la orden las que tengan Cantidad a pedir > 0.
    """
    _name = 'mba.purchase.programada.line'
    _description = 'Selección de productos - Compras Programadas'

    wizard_id = fields.Many2one(
        'mba.purchase.programada.wizard', required=True, ondelete='cascade')
    order_id = fields.Many2one(
        related='wizard_id.order_id', store=True, readonly=True)
    product_id = fields.Many2one('product.product', required=True, readonly=True)

    # Mismo campo/patrón que stock_warehouse_orderpoint.py: Referencia
    # separada de la descripción del producto (MBA Consultings).
    mba_reference = fields.Char(
        related='product_id.default_code', store=True, readonly=True,
        string='Referencia')

    # Mismo patrón que mba_qty_on_hand en purchase_order_line.py: existencia
    # física en el almacén de recepción de la orden, vía el contexto
    # 'warehouse' que ya soporta qty_available. No se guarda (store=True)
    # porque depende del almacén de la orden, que puede cambiar en borrador.
    mba_qty_on_hand = fields.Float(
        string='A la mano',
        compute='_compute_mba_qty_on_hand',
        digits='Product Unit of Measure',
        readonly=True,
        help='Existencia física del producto en el almacén de recepción '
             'de esta orden (Entregar en > Almacén).',
    )

    qty_to_order = fields.Float(
        string='Cantidad a pedir',
        digits='Product Unit of Measure',
        default=0.0,
        help='Cantidad que se agregará a la orden para este producto. '
             'Solo se agregan a la orden los productos con cantidad '
             'mayor a 0 -los que se dejan en 0 se ignoran-, así que '
             'basta con escribir cantidad únicamente en lo que sí se '
             'quiere pedir, sin marcar nada.',
    )

    # Precio sugerido: se precarga con el precio configurado en la pestaña
    # "Compras" del producto para este proveedor (product.supplierinfo),
    # ver PurchaseOrder.action_mba_open_programada_products. El comprador
    # lo puede sobrescribir a mano cuando el proveedor le da un precio
    # especial.
    price_unit = fields.Float(
        string='Precio unitario',
        digits=(16, 2),
        default=0.0,
        help='Precio sugerido según la pestaña "Compras" del producto para '
             'este proveedor. Editable: si el proveedor da un precio '
             'especial, se puede corregir aquí, o directamente en la '
             'columna Subtotal (ver ese campo).',
    )

    # --- MBA: precio especial por lote ---
    # A veces el proveedor no cotiza por unidad sino un total cerrado por
    # el lote/cantidad que se pide ("te lo dejo en $95 los 50"). En vez de
    # obligar al comprador a sacar la división a mano, este campo permite
    # escribir directamente el subtotal que le dieron: la función inverse
    # recalcula price_unit = subtotal / cantidad, redondeado a 2 decimales
    # (pedido explícito del usuario). Si en cambio se edita Precio
    # unitario o Cantidad, el subtotal se recalcula normal (cantidad x
    # precio), como cualquier compute.
    subtotal = fields.Float(
        string='Subtotal',
        digits=(16, 2),
        compute='_compute_subtotal',
        inverse='_inverse_subtotal',
        store=True,
        help='Cantidad x Precio unitario. También se puede escribir al '
             'revés: si el proveedor dio un precio especial por el lote '
             'completo, se anota aquí y el Precio unitario se recalcula '
             'solo (redondeado a 2 decimales).',
    )

    # Mismos campos/patrón que stock_warehouse_orderpoint.py y
    # purchase_order_line.py (módulo mb_stock_orderpoint_vendor): historial
    # de ventas de Sage, rolling window de 4 meses, ya calculado en
    # product.template. Se traen tal cual (related) para dar el mismo
    # contexto que el comprador ya ve en Reabastecimiento y en las líneas
    # de la orden de compra normal.
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

    @api.depends('qty_to_order', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty_to_order * line.price_unit

    def _inverse_subtotal(self):
        for line in self:
            if line.qty_to_order:
                line.price_unit = float_round(
                    line.subtotal / line.qty_to_order, precision_digits=2)
            elif line.subtotal:
                # No hay cantidad todavía: no hay con qué dividir. Se deja
                # el precio en 0 en vez de fallar; el comprador completa la
                # cantidad y puede volver a escribir el subtotal.
                line.price_unit = 0.0
