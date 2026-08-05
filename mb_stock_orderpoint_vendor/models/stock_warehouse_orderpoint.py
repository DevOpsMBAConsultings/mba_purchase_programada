# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    allowed_vendor_ids = fields.Many2many(
        'res.partner',
        compute='_compute_allowed_vendor_ids',
        string="Proveedores Permitidos del Producto",
        help="Proveedores configurados en la pestaña de compras del producto."
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string="Proveedor",
        compute='_compute_vendor_id',
        store=True,
        readonly=False,
        domain="[('id', 'in', allowed_vendor_ids)]",
        help="Proveedor asignado para el reabastecimiento. Por defecto toma el primer proveedor de la lista de compras del producto."
    )

    @api.depends('product_id.seller_ids.partner_id', 'company_id')
    def _compute_allowed_vendor_ids(self):
        for orderpoint in self:
            if orderpoint.product_id and orderpoint.product_id.seller_ids:
                sellers = orderpoint.product_id.seller_ids
                if orderpoint.company_id:
                    sellers = sellers.filtered(
                        lambda s: not s.company_id or s.company_id == orderpoint.company_id
                    )
                orderpoint.allowed_vendor_ids = sellers.mapped('partner_id')
            else:
                orderpoint.allowed_vendor_ids = False

    @api.depends('product_id', 'company_id', 'product_id.seller_ids')
    def _compute_vendor_id(self):
        super()._compute_vendor_id()
        for orderpoint in self:
            if orderpoint.product_id and orderpoint.product_id.seller_ids:
                sellers = orderpoint.product_id.seller_ids
                if orderpoint.company_id:
                    sellers = sellers.filtered(
                        lambda s: not s.company_id or s.company_id == orderpoint.company_id
                    )
                allowed_partners = sellers.mapped('partner_id')
                if allowed_partners:
                    # Si está vacío o el proveedor actual no está entre los configurados para el producto,
                    # asignamos automáticamente el primer proveedor de la lista (ordenado por secuencia)
                    if not orderpoint.vendor_id or orderpoint.vendor_id not in allowed_partners:
                        orderpoint.vendor_id = allowed_partners[0]
                else:
                    orderpoint.vendor_id = False
            elif not orderpoint.product_id or not orderpoint.product_id.seller_ids:
                orderpoint.vendor_id = False
