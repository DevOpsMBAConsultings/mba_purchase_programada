from odoo import models, api

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        if report.report_name in ('account.report_invoice_with_payments', 'account.report_invoice'):
            if res_ids and len(res_ids) == 1:
                move = self.env['account.move'].browse(res_ids[0])
                if hasattr(move, 'l10n_pa_pac_status') and move.l10n_pa_pac_status == 'accepted':
                    att = self.env['ir.attachment'].search([
                        ('res_model', '=', 'account.move'),
                        ('res_id', '=', move.id),
                        ('name', 'ilike', '%_CAFE.pdf')
                    ], limit=1)
                    if att:
                        import base64
                        return base64.b64decode(att.datas), 'pdf'
                        
        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
