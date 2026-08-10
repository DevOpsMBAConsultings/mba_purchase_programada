# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseProgramadaWizard(models.TransientModel):
    """Pantalla de selección de productos para Compras Programadas.

    Se muestran TODOS los productos del proveedor de una vez (campo
    line_ids, editable en pantalla) -sin checkboxes que marcar-, y el
    botón "Agregar productos" del pie de página siempre está disponible
    (no depende de ninguna selección): al presionarlo, revisa todas las
    filas y agrega a la orden únicamente las que tengan Cantidad a pedir
    mayor a 0.
    """
    _name = 'mba.purchase.programada.wizard'
    _description = 'Selección de productos - Compras Programadas'

    order_id = fields.Many2one('purchase.order', required=True)
    line_ids = fields.One2many(
        'mba.purchase.programada.line', 'wizard_id', string='Productos')

    def action_add_to_order(self):
        self.ensure_one()
        lines_to_add = self.line_ids.filtered(lambda line: line.qty_to_order > 0)
        if not lines_to_add:
            return {'type': 'ir.actions.act_window_close'}

        order = self.order_id

        PurchaseOrderLine = self.env['purchase.order.line']
        new_lines = self.env['purchase.order.line']
        for line in lines_to_add:
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

        return {'type': 'ir.actions.act_window_close'}
