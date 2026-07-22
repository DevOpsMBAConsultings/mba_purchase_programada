# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    social_facebook = fields.Char(string='Facebook', help='Enlace a la página de Facebook')
    social_instagram = fields.Char(string='Instagram', help='Enlace a la cuenta de Instagram')
    social_linkedin = fields.Char(string='LinkedIn', help='Enlace al perfil de LinkedIn')
