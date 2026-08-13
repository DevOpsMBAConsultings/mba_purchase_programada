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

    def _mba_get_programada_supplierinfos(self):
        """product.supplierinfo de self.partner_id, ya filtradas por
        compañía. Es la fuente única tanto del universo de productos a
        ofrecer como del precio sugerido de cada uno (ver
        action_mba_open_programada_products): al traerlas una sola vez
        evitamos dos búsquedas separadas que podrían desalinearse.
        """
        self.ensure_one()
        if not self.partner_id:
            return self.env['product.supplierinfo']

        company_id = self.company_id.id or self.env.company.id
        return self.env['product.supplierinfo'].search([
            ('partner_id', '=', self.partner_id.id),
            ('company_id', 'in', [False, company_id]),
        ])

    def _mba_get_programada_supplier_products(self):
        """Productos comprables y activos que tengan a self.partner_id
        configurado como proveedor en su pestaña "Compras" (product.
        supplierinfo), y que todavía no estén en las líneas de esta orden.

        Es el "universo" que se ofrece para elegir en la pantalla de
        selección (ver mba.purchase.programada.line); no se agrega nada
        a la orden automáticamente.
        """
        supplierinfos = self._mba_get_programada_supplierinfos()

        products = self.env['product.product']
        for supplierinfo in supplierinfos:
            if supplierinfo.product_id:
                products |= supplierinfo.product_id
            elif supplierinfo.product_tmpl_id:
                products |= supplierinfo.product_tmpl_id.product_variant_ids

        products = products.filtered(lambda p: p.active and p.purchase_ok)
        return products - self.order_line.product_id

    def action_mba_open_programada_products(self):
        """Abre la pantalla de selección de productos del proveedor: se
        muestran todos de una vez (sin checkboxes que marcar) y el
        comprador solo escribe cantidad en los que quiere pedir este mes;
        el botón "Agregar productos" del wizard agrega a la orden
        únicamente los que quedaron con cantidad > 0.
        """
        self.ensure_one()
        Wizard = self.env['mba.purchase.programada.wizard']
        # Limpia una selección previa de esta misma orden, por si el
        # comprador abre la pantalla más de una vez (evita duplicados).
        Wizard.search([('order_id', '=', self.id)]).unlink()

        supplierinfos = self._mba_get_programada_supplierinfos()

        # Precio sugerido por producto: la primera product.supplierinfo
        # que lo incluya (ya vienen ordenadas por sequence/min_qty/price,
        # orden por defecto del modelo -ver product.supplierinfo._order-,
        # así que la primera es la de mayor prioridad para ese proveedor).
        price_by_product = {}
        products = self.env['product.product']
        for supplierinfo in supplierinfos:
            supplier_products = (
                supplierinfo.product_id
                or (supplierinfo.product_tmpl_id.product_variant_ids
                    if supplierinfo.product_tmpl_id else self.env['product.product'])
            )
            for product in supplier_products:
                price_by_product.setdefault(product.id, supplierinfo.price)
            products |= supplier_products

        products = products.filtered(
            lambda p: p.active and p.purchase_ok) - self.order_line.product_id

        wizard = Wizard.create({
            'order_id': self.id,
            'line_ids': [
                (0, 0, {
                    'product_id': product.id,
                    'price_unit': price_by_product.get(product.id, 0.0),
                })
                for product in products
            ],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Seleccionar productos del proveedor'),
            'res_model': 'mba.purchase.programada.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
