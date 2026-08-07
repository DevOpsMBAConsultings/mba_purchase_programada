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

    # --- MBA: Historial de ventas de Sage (rolling window 4 meses) ---
    mba_sold_m1 = fields.Float(
        related='product_tmpl_id.mba_sold_m1', store=True, readonly=True)
    mba_sold_m2 = fields.Float(
        related='product_tmpl_id.mba_sold_m2', store=True, readonly=True)
    mba_sold_m3 = fields.Float(
        related='product_tmpl_id.mba_sold_m3', store=True, readonly=True)
    mba_sold_m4 = fields.Float(
        related='product_tmpl_id.mba_sold_m4', store=True, readonly=True)
    mba_sold_total_4m = fields.Float(
        related='product_tmpl_id.mba_sold_total_4m', store=True, readonly=True)
    mba_label_m1 = fields.Char(
        related='product_tmpl_id.mba_label_m1', store=True, readonly=True)
    mba_label_m2 = fields.Char(
        related='product_tmpl_id.mba_label_m2', store=True, readonly=True)
    mba_label_m3 = fields.Char(
        related='product_tmpl_id.mba_label_m3', store=True, readonly=True)
    mba_label_m4 = fields.Char(
        related='product_tmpl_id.mba_label_m4', store=True, readonly=True)

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
