# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    supplier_id = fields.Many2one(
        'product.supplierinfo',
        compute='_compute_supplier_id',
        store=True,
        readonly=False
    )

    @api.depends('product_id', 'product_tmpl_id.seller_ids', 'company_id')
    def _compute_supplier_id(self):
        for orderpoint in self:
            if orderpoint.product_tmpl_id and orderpoint.product_tmpl_id.seller_ids:
                sellers = orderpoint.product_tmpl_id.seller_ids
                if orderpoint.company_id:
                    sellers = sellers.filtered(
                        lambda s: not s.company_id or s.company_id == orderpoint.company_id
                    )
                if sellers:
                    if not orderpoint.supplier_id or orderpoint.supplier_id not in sellers:
                        orderpoint.supplier_id = sellers[0]
                else:
                    if not orderpoint.supplier_id or orderpoint.supplier_id.product_tmpl_id != orderpoint.product_tmpl_id:
                        orderpoint.supplier_id = False
            else:
                if not orderpoint.supplier_id or orderpoint.supplier_id.product_tmpl_id != orderpoint.product_tmpl_id:
                    orderpoint.supplier_id = False
