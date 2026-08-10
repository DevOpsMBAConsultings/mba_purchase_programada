# -*- coding: utf-8 -*-

from odoo import Command, api, fields, models


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
             'desde el menú "Compras Programadas", que precarga automáticamente '
             'los productos configurados con ese proveedor.',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_mba_programada(self):
        """Al elegir proveedor en una compra programada, precargar todas las
        líneas de producto que tengan a ese proveedor configurado en la
        pestaña "Compras" de la ficha del producto (product.supplierinfo).

        La cantidad se deja en 0 para que el comprador la complete a mano.
        El resto de campos de la línea (precio, UdM, impuestos, descripción,
        fecha prevista) se completan solos: al agregar la línea únicamente
        con product_id, se dispara en cascada el propio onchange de
        product_id de purchase.order.line (el mismo que corre cuando el
        usuario agrega el producto manualmente desde "Agregar un producto").
        """
        if self.mba_order_type != 'programada' or not self.partner_id:
            return

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

        # Solo productos comprables y activos; y no duplicar los que ya
        # estén en la orden (p. ej. si el usuario cambia de proveedor y
        # vuelve a seleccionar el mismo, o agregó algo a mano antes).
        products = products.filtered(lambda p: p.active and p.purchase_ok)
        new_products = products - self.order_line.product_id
        if new_products:
            self.order_line = [
                Command.create({'product_id': product.id, 'product_qty': 0})
                for product in new_products
            ]
