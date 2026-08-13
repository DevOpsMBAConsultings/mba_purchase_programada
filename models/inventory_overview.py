# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, time


class MbaInventoryOverview(models.Model):
    _name = 'mba.inventory.overview'
    _description = 'Métricas de Inventario Operativo'

    name = fields.Char("Nombre", default="Inventario Operativo")
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)
    fisico_bruto = fields.Float("Físico en Bodega", compute="_compute_metrics", store=True)
    deficit_negativo = fields.Float("Déficit Vtas. Negativas", compute="_compute_metrics", store=True)
    compras_transito = fields.Float("Compras en Tránsito", compute="_compute_metrics", store=True)
    inventario_operativo = fields.Float("Inv. Operativo Proyectado", compute="_compute_metrics", store=True)

    @api.depends('company_id')
    def _compute_metrics(self):
        today = fields.Date.context_today(self)
        date_start = datetime.combine(today, time.min)
        date_end = datetime.combine(today, time.max)

        for rec in self:
            company = rec.company_id or self.env.company
            wizard = self.env['mba.daily.pos.wizard'].new({
                'date_report': today,
                'period_type': 'day',
                'company_id': company.id,
            })
            res = wizard._get_cost_and_inventory(date_start, date_end, 0.0)

            rec.fisico_bruto = res.get('fisico_bruto', 0.0)
            rec.deficit_negativo = res.get('deficit_negativo', 0.0)
            rec.compras_transito = res.get('compras_transito', 0.0)
            rec.inventario_operativo = res.get('inventario_operativo', 0.0)

    def action_refresh_metrics(self):
        """Método para forzar el recálculo y actualización inmediata de las métricas almacenadas."""
        self._compute_metrics()

    def init(self):
        """Asegura que exista un registro inicial por empresa al instalar/actualizar."""
        super().init()
        for company in self.env['res.company'].search([]):
            rec = self.search([('company_id', '=', company.id)], limit=1)
            if not rec:
                rec = self.create({'name': 'Inventario Operativo', 'company_id': company.id})
            rec._compute_metrics()
