# -*- coding: utf-8 -*-
"""
Extiende res.company solo con el método que dispara el re-sync del tema
de marca (ver ../hooks.py). Existe porque data/ir_actions_server.xml no
puede importar hooks.py directamente: el código de una ir.actions.server
corre dentro del sandbox safe_eval de Odoo, que bloquea cualquier
import/from...import. Un método de modelo normal, en cambio, se importa
como Python normal (sin sandbox) y se puede LLAMAR desde la server action
sin problema (record.action_resync_brand_theme()).
"""
from odoo import models

from ..hooks import _apply_brand_theme


class ResCompany(models.Model):
    _inherit = "res.company"

    def action_resync_brand_theme(self):
        """Vuelve a aplicar el color de marca de cada empresa en self a
        los estilos de los reportes MIS. Pensado para llamarse desde la
        acción contextual de la ficha de Empresa, pero también sirve
        para múltiples empresas a la vez si se llama en lote."""
        for company in self:
            _apply_brand_theme(self.env, company=company)
