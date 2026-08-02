from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_aging_bucket_1 = fields.Integer(
        related="company_id.account_aging_bucket_1", readonly=False
    )
    account_aging_bucket_2 = fields.Integer(
        related="company_id.account_aging_bucket_2", readonly=False
    )
    account_aging_bucket_3 = fields.Integer(
        related="company_id.account_aging_bucket_3", readonly=False
    )
