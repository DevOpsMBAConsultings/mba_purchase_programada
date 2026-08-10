# -*- coding: utf-8 -*-

from odoo import api, fields, models


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

    @api.depends('product_id', 'order_id.picking_type_id.warehouse_id')
    def _compute_mba_qty_on_hand(self):
        for line in self:
            warehouse = line.order_id.picking_type_id.warehouse_id
            if line.product_id and warehouse:
                line.mba_qty_on_hand = line.product_id.with_context(
                    warehouse=warehouse.id).qty_available
            else:
                line.mba_qty_on_hand = 0.0

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
            })

        # price_unit / name / date_planned / discount son campos
        # computados y guardados (compute='_compute_price_unit_and_date_
        # planned_and_name' en purchase.order.line del core) y se llenan
        # solos al crear la línea. taxes_id NO es un campo computado ahí
        # -solo se llena vía el onchange de product_id en pantalla-, así
        # que reutilizamos el mismo método que usa ese onchange
        # (_compute_tax_id) para no reinventar el mapeo de posición fiscal.
        if new_lines:
            new_lines._compute_tax_id()

        # Limpieza: ya no hace falta la selección de esta orden.
        self.env['mba.purchase.programada.line'].search(
            [('order_id', '=', order.id)]).unlink()

        return {'type': 'ir.actions.act_window_close'}
