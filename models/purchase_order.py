# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # --- MBA: Compras Programadas ---
    # Mismo modelo/flujo que una orden de compra normal (purchase.order):
    # no se crea un modelo aparte para no duplicar UI ni perder las
    # columnas ya agregadas por mb_stock_orderpoint_vendor. Este campo solo
    # sirve para distinguir/filtrar en reportes las compras mensuales
    # (recurrentes a un proveedor) de las transaccionales (puntuales, p.ej.
    # asociadas a una venta).
    mba_order_type = fields.Selection(
        selection=[
            ('transactional', 'Transaccional'),
            ('programada', 'Programada'),
        ],
        string='Tipo de orden',
        default='transactional',
        required=True,
        help='Transaccional: compra puntual (p. ej. asociada a una venta).\n'
             'Programada: compra mensual/recurrente a un proveedor, generada '
             'desde el menú "Compras Programadas".',
    )

    def _mba_get_programada_supplier_products(self):
        """Productos comprables y activos que tengan a self.partner_id
        configurado como proveedor en su pestaña "Compras" (product.
        supplierinfo), y que todavía no estén en las líneas de esta orden.

        Es el "universo" que se ofrece para elegir en la pantalla de
        selección (ver mba.purchase.programada.line); no se agrega nada
        a la orden automáticamente.
        """
        self.ensure_one()
        if not self.partner_id:
            return self.env['product.product']

        company_id = self.company_id.id or self.env.company.id
        supplierinfos = self.env['product.supplierinfo'].search([
            ('partner_id', '=', self.partner_id.id),
            ('company_id', 'in', [False, company_id]),
        ])

        products = self.env['product.product']
        for supplierinfo in supplierinfos:
            if supplierinfo.product_id:
                products |= supplierinfo.product_id
            elif supplierinfo.product_tmpl_id:
                products |= supplierinfo.product_tmpl_id.product_variant_ids

        products = products.filtered(lambda p: p.active and p.purchase_ok)
        return products - self.order_line.product_id

    def action_mba_open_programada_products(self):
        """Abre la pantalla de selección de productos del proveedor
        (lista con checkboxes + cantidad editable, igual en espíritu a
        Reabastecimiento en Inventario): el comprador marca las filas que
        quiere pedir este mes y define cuánto, y solo esas se agregan a
        la orden con el botón "Agregar a la orden" de esa lista.
        """
        self.ensure_one()
        Line = self.env['mba.purchase.programada.line']
        # Limpia una selección previa de esta misma orden, por si el
        # comprador abre la pantalla más de una vez (evita duplicados).
        Line.search([('order_id', '=', self.id)]).unlink()

        products = self._mba_get_programada_supplier_products()
        lines = Line.create([
            {'order_id': self.id, 'product_id': product.id}
            for product in products
        ])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Seleccionar productos del proveedor'),
            'res_model': 'mba.purchase.programada.line',
            'view_mode': 'list',
            'domain': [('id', 'in', lines.ids)],
            'target': 'new',
        }
