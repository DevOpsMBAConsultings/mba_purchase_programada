from odoo import _, fields, models

DEFAULT_BUCKETS = (30, 60, 90)


class AccountAgingAnalysis(models.Model):
    """Read-only SQL view exposing open receivable and payable items,
    classified into ageing buckets by number of days past due.

    Buckets are computed in SQL against ``CURRENT_DATE`` on every query, so
    the result is never stale and no scheduled recomputation is required.
    Bucket boundaries are read from the company configuration, which means
    each company in a multi-company database can use its own thresholds.
    """

    _name = "account.aging.analysis"
    _description = "Aged Balance Analysis"
    _auto = False
    _order = "days_overdue desc"
    _rec_name = "move_name"

    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True)
    move_name = fields.Char(string="Document", readonly=True)
    ref = fields.Char(string="Reference", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    commercial_partner_id = fields.Many2one(
        "res.partner", string="Commercial Entity", readonly=True
    )
    invoice_user_id = fields.Many2one("res.users", string="Salesperson", readonly=True)
    account_id = fields.Many2one("account.account", string="Account", readonly=True)
    journal_id = fields.Many2one("account.journal", string="Journal", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True)

    ledger = fields.Selection(
        [("receivable", "Receivable"), ("payable", "Payable")],
        string="Ledger",
        readonly=True,
    )
    date = fields.Date(string="Date", readonly=True)
    date_maturity = fields.Date(string="Due Date", readonly=True)
    days_overdue = fields.Integer(string="Days Overdue", readonly=True)
    aging_bucket = fields.Selection(
        selection="_selection_aging_bucket", string="Ageing Bucket", readonly=True
    )
    amount_residual = fields.Monetary(
        string="Amount Due", currency_field="currency_id", readonly=True
    )

    def _selection_aging_bucket(self):
        """Bucket labels follow the thresholds configured on the company."""
        company = self.env.company
        b1 = company.account_aging_bucket_1 or DEFAULT_BUCKETS[0]
        b2 = company.account_aging_bucket_2 or DEFAULT_BUCKETS[1]
        b3 = company.account_aging_bucket_3 or DEFAULT_BUCKETS[2]
        return [
            ("not_due", _("Not due")),
            ("bucket_1", _("1 - %s days", b1)),
            ("bucket_2", _("%(start)s - %(end)s days", start=b1 + 1, end=b2)),
            ("bucket_3", _("%(start)s - %(end)s days", start=b2 + 1, end=b3)),
            ("bucket_4", _("Older than %s days", b3)),
        ]

    @property
    def _table_query(self):
        return """
            SELECT
                aml.id                                  AS id,
                aml.move_id                             AS move_id,
                am.name                                 AS move_name,
                aml.ref                                 AS ref,
                aml.partner_id                          AS partner_id,
                rp.commercial_partner_id                AS commercial_partner_id,
                am.invoice_user_id                      AS invoice_user_id,
                aml.account_id                          AS account_id,
                aml.journal_id                          AS journal_id,
                aml.company_id                          AS company_id,
                rc.currency_id                          AS currency_id,
                aml.date                                AS date,
                COALESCE(aml.date_maturity, aml.date)   AS date_maturity,
                CASE
                    WHEN aa.account_type = 'asset_receivable' THEN 'receivable'
                    ELSE 'payable'
                END                                     AS ledger,
                GREATEST(
                    (CURRENT_DATE - COALESCE(aml.date_maturity, aml.date))::int, 0
                )                                       AS days_overdue,
                CASE
                    WHEN COALESCE(aml.date_maturity, aml.date) >= CURRENT_DATE
                        THEN 'not_due'
                    WHEN (CURRENT_DATE - COALESCE(aml.date_maturity, aml.date))
                        <= COALESCE(rc.account_aging_bucket_1, 30)
                        THEN 'bucket_1'
                    WHEN (CURRENT_DATE - COALESCE(aml.date_maturity, aml.date))
                        <= COALESCE(rc.account_aging_bucket_2, 60)
                        THEN 'bucket_2'
                    WHEN (CURRENT_DATE - COALESCE(aml.date_maturity, aml.date))
                        <= COALESCE(rc.account_aging_bucket_3, 90)
                        THEN 'bucket_3'
                    ELSE 'bucket_4'
                END                                     AS aging_bucket,
                CASE
                    WHEN aa.account_type = 'liability_payable'
                        THEN -aml.amount_residual
                    ELSE aml.amount_residual
                END                                     AS amount_residual
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN res_company rc ON rc.id = aml.company_id
            LEFT JOIN res_partner rp ON rp.id = aml.partner_id
            WHERE aa.account_type IN ('asset_receivable', 'liability_payable')
              AND am.state = 'posted'
              AND aml.full_reconcile_id IS NULL
              AND aml.amount_residual != 0
        """
