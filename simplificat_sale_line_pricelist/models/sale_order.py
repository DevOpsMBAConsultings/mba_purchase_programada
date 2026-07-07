from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # We do not strictly need to override anything here unless we want to bypass global pricelist validations.
    # The requirement is just to hide it in the view and move the pricelist logic to the line.
