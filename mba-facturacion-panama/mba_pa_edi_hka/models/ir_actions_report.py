import base64

from odoo import models, api


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _pre_render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """
        Sustituye el PDF generico por el CAFE (Comprobante Auxiliar de
        Factura Electronica) real que devolvio el PAC (HKA), cuando la
        factura ya fue aceptada por la DGI.

        NOTA - bug de compatibilidad corregido: en Odoo <=16 este override
        vivia sobre '_render_qweb_pdf'. En Odoo 18 esa ya NO es la funcion
        que arma el PDF de una factura: account_move_send.py (core) llama
        a '_pre_render_qweb_pdf' (ver linea ~384), y 'account/models/
        ir_actions_report.py' (core) ya extiende justamente ese metodo, no
        '_render_qweb_pdf'. Con el nombre viejo, este override nunca se
        ejecutaba: SIEMPRE se servia el PDF generico de Odoo (o el cacheado
        en 'invoice_pdf_report_id'), nunca el CAFE con CUFE/QR del PAC,
        aunque la factura ya estuviera aceptada. Firma y contrato de
        retorno (content, report_type) son los mismos que el metodo viejo,
        asi que el cuerpo no cambia, solo el nombre del metodo.
        """
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
                        return base64.b64decode(att.datas), 'pdf'

        return super()._pre_render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
