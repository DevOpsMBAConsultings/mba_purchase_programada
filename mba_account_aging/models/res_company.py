from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    account_aging_bucket_1 = fields.Integer(
        string="First Ageing Bucket (days)",
        default=30,
        help="Upper bound, in days past due, of the first ageing bucket.",
    )
    account_aging_bucket_2 = fields.Integer(
        string="Second Ageing Bucket (days)",
        default=60,
        help="Upper bound, in days past due, of the second ageing bucket.",
    )
    account_aging_bucket_3 = fields.Integer(
        string="Third Ageing Bucket (days)",
        default=90,
        help="Upper bound, in days past due, of the third ageing bucket. "
        "Anything older falls into the last bucket.",
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
                    _("The first ageing bucket must be at least 1 day.")
                )
            if not bounds[0] < bounds[1] < bounds[2]:
                raise ValidationError(
                    _(
                        "Ageing buckets must be strictly increasing "
                        "(for example 30, 60 and 90 days)."
                    )
                )
