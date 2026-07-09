# -*- coding: utf-8 -*-
from odoo import models


class AccountMoveSend(models.AbstractModel):
    """
    Inyecta el PDF CAFE de la DGI (HKA) en el wizard de envío de correo
    en lugar del PDF generado por Odoo, cuando la factura está aceptada por el PAC.
    """
    _inherit = "account.move.send"

    def _get_invoice_extra_attachments(self, move):
        """
        Devuelve el adjunto CAFE PDF de HKA si la factura está aceptada.
        Este método es usado por Odoo para incluir adjuntos adicionales en el wizard de envío.
        """
        if (
            move.move_type in ("out_invoice", "out_refund")
            and getattr(move, "l10n_pa_pac_status", None) == "accepted"
        ):
            cafe_att = self.env["ir.attachment"].search([
                ("res_model", "=", "account.move"),
                ("res_id", "=", move.id),
                ("name", "ilike", "%_CAFE.pdf"),
            ], limit=1)
            if cafe_att:
                return cafe_att
        return super()._get_invoice_extra_attachments(move)

    def _get_placeholder_mail_attachments_data(self, move, invoice_edi_format=None, extra_edis=None, pdf_report=None):
        """
        Evita que Odoo muestre un placeholder genérico de PDF cuando ya tenemos
        el CAFE PDF de HKA adjunto.
        """
        if (
            move.move_type in ("out_invoice", "out_refund")
            and getattr(move, "l10n_pa_pac_status", None) == "accepted"
        ):
            cafe_att = self.env["ir.attachment"].search([
                ("res_model", "=", "account.move"),
                ("res_id", "=", move.id),
                ("name", "ilike", "%_CAFE.pdf"),
            ], limit=1)
            if cafe_att:
                return []
        return super()._get_placeholder_mail_attachments_data(
            move,
            invoice_edi_format=invoice_edi_format,
            extra_edis=extra_edis,
            pdf_report=pdf_report,
        )
