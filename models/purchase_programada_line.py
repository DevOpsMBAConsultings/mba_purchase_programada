# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class PurchaseProgramadaLine(models.TransientModel):
    """Pantalla de selección de productos para Compras Programadas.

    Una fila por cada producto que tiene al proveedor de la orden
    configurado en su pestaña "Compras" (product.supplierinfo). Se abre
    como una lista (no un formulario) para poder usar la selección nativa
    de Odoo con checkboxes + un botón de acción masiva "Agregar a la
    orden", igual en espíritu a la pantalla de Reabastecimiento en
    Inventario (stock.warehouse.orderpoint): marcar filas, definir
    cantidad y confirmar.
    """
    _name = 'mba.purchase.programada.line'
    _description = 'Selección de productos - Compras Programadas'

    order_id = fields.Many2one('purchase.order', required=True, ondelete='cascade')
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
        help='Cantidad que se agregará a la orden para este producto si '
             'la fila queda seleccionada.',
    )

    # Precio sugerido: se precarga con el precio configurado en la pestaña
    # "Compras" del producto para este proveedor (product.supplierinfo),
    # ver action_mba_open_programada_products. El comprador lo puede
    # sobrescribir a mano cuando el proveedor le da un precio especial.
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
                # No hay cantidad todavía: no hay con qué dividir. Se dejar
                # el precio en 0 en vez de fallar; el comprador completa la
                # cantidad y puede volver a escribir el subtotal.
                line.price_unit = 0.0

    def action_add_to_order(self):
        """Botón de acción masiva de la lista: self son solo las filas
        marcadas por el usuario (selección nativa de Odoo), no todas las
        que se muestran en pantalla.
        """
        if not self:
            return {'type': 'ir.actions.act_window_close'}

        order = self.mapped('order_id')
        order.ensure_one()

        PurchaseOrderLine = self.env['purchase.order.line']
        new_lines = self.env['purchase.order.line']
        for line in self:
            product = line.product_id
            uom = product.uom_po_id or product.uom_id
            new_lines |= PurchaseOrderLine.create({
                'order_id': order.id,
                'product_id': product.id,
                'product_qty': line.qty_to_order,
                'product_uom': uom.id,
                # Se pasa explícito (no se deja que el compute del core lo
                # calcule solo) porque el comprador pudo haber puesto un
                # precio especial acá, distinto al de la ficha del
                # proveedor.
                'price_unit': line.price_unit,
            })

        # name / date_planned / discount son campos computados y guardados
        # (compute='_compute_price_unit_and_date_planned_and_name' en
        # purchase.order.line del core) y se llenan solos al crear la
        # línea -price_unit ya lo fijamos arriba, así que ese compute no lo
        # toca-. taxes_id NO es un campo computado ahí -solo se llena vía
        # el onchange de product_id en pantalla-, así que reutilizamos el
        # mismo método que usa ese onchange (_compute_tax_id) para no
        # reinventar el mapeo de posición fiscal.
        if new_lines:
            new_lines._compute_tax_id()

        # Limpieza: ya no hace falta la selección de esta orden.
        self.env['mba.purchase.programada.line'].search(
            [('order_id', '=', order.id)]).unlink()

        return {'type': 'ir.actions.act_window_close'}
