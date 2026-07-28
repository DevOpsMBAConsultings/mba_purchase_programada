# Copyright 2022 Camptocamp SA
# Copyright 2026 MBA Consultings
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade_merge_records

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MergePurchaseAutomatic(models.TransientModel):
    """
    Wizard to merge purchase orders.

    The idea behind this wizard is to create a list of potential purchases
    to merge. Allows merging draft POs from the same supplier with identical
    terms, and optionally delete or cancel source POs.
    """

    _name = "purchase.merge.automatic.wizard"
    _description = "Purchase Order Consolidation Wizard"

    purchase_ids = fields.Many2many(
        comodel_name="purchase.order",
        string="Purchase Orders to Merge",
    )
    dst_purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Destination Purchase Order",
    )
    delete_source_po = fields.Boolean(
        string="Delete Source Purchase Orders",
        default=False,
        help="If checked, source POs will be deleted after merge. "
        "If unchecked, they will only be cancelled.",
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-populate the wizard with selected POs."""
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids", [])

        if (
            self.env.context.get("active_model") == "purchase.order"
            and len(active_ids) >= 1
        ):
            purchase_orders = self.env["purchase.order"].browse(active_ids)
            self._check_all_values(purchase_orders)
            res["purchase_ids"] = [(6, 0, active_ids)]
            res["dst_purchase_id"] = self._get_ordered_purchase(active_ids)[-1].id

        return res

    # ----------------------------------------
    # Validation Methods
    # ----------------------------------------

    def _check_all_values(self, purchase_orders):
        """Run all validation checks."""
        self._check_state(purchase_orders)
        self._check_content(purchase_orders)

    def _check_state(self, purchase_orders):
        """Ensure all POs are in draft state."""
        non_draft_po = purchase_orders.filtered(lambda p: p.state != "draft")
        if non_draft_po:
            po_names = non_draft_po.mapped("name")
            raise ValidationError(
                _("Cannot merge purchase orders not in draft state: %s")
                % ", ".join(po_names)
            )

    def _check_content(self, purchase_orders):
        """Validate that POs have compatible terms."""
        error_messages = []

        # Check currency
        currencies = purchase_orders.currency_id
        if len(currencies) > 1:
            error_messages.append(
                _("Purchase orders have different currencies: %s")
                % ", ".join(currencies.mapped("name"))
            )

        # Check picking type
        picking_types = purchase_orders.picking_type_id
        if len(picking_types) > 1:
            error_messages.append(
                _("Purchase orders have different picking types: %s")
                % ", ".join(picking_types.mapped("name"))
            )

        # Check incoterms
        incoterms = purchase_orders.incoterm_id
        if len(incoterms) > 1:
            error_messages.append(
                _("Purchase orders have different incoterms: %s")
                % ", ".join(incoterms.mapped("name"))
            )

        # Check payment terms
        payment_terms = purchase_orders.payment_term_id
        if len(payment_terms) > 1:
            error_messages.append(
                _("Purchase orders have different payment terms: %s")
                % ", ".join(payment_terms.mapped("name"))
            )

        # Check fiscal position
        fiscal_positions = purchase_orders.fiscal_position_id
        if len(fiscal_positions) > 1:
            error_messages.append(
                _("Purchase orders have different fiscal positions: %s")
                % ", ".join(fiscal_positions.mapped("name"))
            )

        # Check supplier
        suppliers = purchase_orders.partner_id
        if len(suppliers) > 1:
            error_messages.append(
                _("Purchase orders are from different suppliers: %s")
                % ", ".join(suppliers.mapped("name"))
            )

        if error_messages:
            raise ValidationError("\n".join(error_messages))

    # ----------------------------------------
    # Merge Logic
    # ----------------------------------------

    @api.model
    def _update_values(self, src_purchase, dst_purchase):
        """
        Transfer all lines and metadata from source to destination PO.

        :param src_purchase: recordset of source purchase.order
        :param dst_purchase: record of destination purchase.order
        """
        dst_purchase.write(self._get_update_values(src_purchase, dst_purchase))

        # Post messages
        for po in src_purchase:
            self._add_message("to", [dst_purchase.name], po)

        po_names = src_purchase.mapped("name")
        self._add_message("from", po_names, dst_purchase)

    @api.model
    def _get_update_values(self, src_purchase, dst_purchase):
        """
        Generate the values to write to destination PO.

        Merges origin and partner_ref fields, and moves all order lines.

        :param src_purchase: recordset of source purchase.order
        :param dst_purchase: record of destination purchase.order
        """
        # Merge origin field
        origin = {dst_purchase.origin or ""}
        origin.update({x.origin for x in src_purchase if x.origin})

        # Merge partner_ref field
        partner_ref = {dst_purchase.partner_ref or ""}
        partner_ref.update({x.partner_ref for x in src_purchase if x.partner_ref})

        # Collect all order lines
        src_order_line = src_purchase.mapped("order_line")
        order_lines = [(4, line.id, 0) for line in src_order_line]

        return {
            "order_line": order_lines,
            "origin": ", ".join(origin),
            "partner_ref": ", ".join(partner_ref),
        }

    def _add_message(self, way, po_names, po):
        """
        Post a message to PO chatter about the merge.

        :param way: 'to' or 'from' indicating direction
        :param po_names: list of PO names involved in merge
        :param po: purchase.order to post message on
        """
        subject = _("Purchase Orders Consolidated")
        if way == "to":
            body = _(
                "Lines from the following purchase orders have been merged into this one: %s"
            ) % ", ".join(po_names)
        else:
            body = _(
                "Lines from this purchase order have been merged into: %s"
            ) % ", ".join(po_names)

        po.message_post(body=body, subject=subject)

    def _merge(self, purchases, dst_purchase=None):
        """
        Execute the merge operation.

        :param purchases: recordset of purchase.order to merge
        :param dst_purchase: destination purchase.order (default: most recent)
        """
        if len(purchases) < 2:
            return

        self._check_all_values(purchases)

        # Determine source and destination
        if dst_purchase and dst_purchase in purchases:
            src_purchase = purchases - dst_purchase
        else:
            ordered = self._get_ordered_purchase(purchases.ids)
            dst_purchase = ordered[-1]
            src_purchase = ordered[:-1]

        # Merge records (OCA utility)
        openupgrade_merge_records.merge_records(
            env=self.env,
            model_name="purchase.order",
            record_ids=src_purchase.ids,
            target_record_id=dst_purchase.id,
            delete=False,
        )

        # Transfer lines and metadata
        self._update_values(src_purchase, dst_purchase)

        # Handle source POs: delete or cancel
        if self.delete_source_po:
            src_purchase.unlink()
        else:
            src_purchase.button_cancel()

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    @api.model
    def _get_ordered_purchase(self, purchase_ids):
        """
        Sort purchase orders by creation date (newest first).

        :param purchase_ids: list of purchase order IDs
        :return: sorted recordset
        """
        return (
            self.env["purchase.order"]
            .browse(purchase_ids)
            .sorted(
                key=lambda p: (p.create_date or ""),
                reverse=True,
            )
        )

    # ----------------------------------------
    # Actions
    # ----------------------------------------

    def action_merge(self):
        """Execute the consolidation."""
        if not self.purchase_ids:
            return False

        self._merge(self.purchase_ids, self.dst_purchase_id)
        return True
