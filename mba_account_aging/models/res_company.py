from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    account_aging_bucket_1 = fields.Integer(
        string="Primer tramo de antigüedad (días)",
        default=30,
        help="Límite superior, en días vencidos, del primer tramo.",
    )
    account_aging_bucket_2 = fields.Integer(
        string="Segundo tramo de antigüedad (días)",
        default=60,
        help="Límite superior, en días vencidos, del segundo tramo.",
    )
    account_aging_bucket_3 = fields.Integer(
        string="Tercer tramo de antigüedad (días)",
        default=90,
        help="Límite superior, en días vencidos, del tercer tramo. "
        "Todo lo más antiguo cae en el último tramo.",
    )

    @api.constrains(
        "account_aging_bucket_1",
        "account_aging_bucket_2",
        "account_aging_bucket_3",
    )
    def _check_account_aging_buckets(self):
        for company in self:
            bounds = (
                company.account_aging_bucket_1,
                company.account_aging_bucket_2,
                company.account_aging_bucket_3,
            )
            if bounds[0] < 1:
                raise ValidationError(
                    _("El primer tramo de antigüedad debe ser de al menos 1 día.")
                )
            if not bounds[0] < bounds[1] < bounds[2]:
                raise ValidationError(
                    _(
                        "Los tramos de antigüedad deben ser estrictamente "
                        "crecientes (por ejemplo 30, 60 y 90 días)."
                    )
                )
