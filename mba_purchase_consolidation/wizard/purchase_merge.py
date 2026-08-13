# Copyright 2022 Camptocamp SA
# Copyright 2026 MBA Consultings
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# Models whose references to the source purchase orders are handled explicitly
# elsewhere (order lines are moved by ``_get_update_values``) or that must never
# be touched (external identifiers).
MERGE_EXCLUDED_MODELS = {
    "purchase.order.line",
    "ir.model.data",
}


class MergePurchaseAutomatic(models.TransientModel):
    """
    The idea behind this wizard is to create a list of potential purchases
    to merge. We use two objects, the first one is the wizard for
    the end-user. And the second will contain the purchase list to merge.
    """

    _name = "purchase.merge.automatic.wizard"
    _description = "Purchase Merge Automatic Wizard"

    purchase_ids = fields.Many2many(
        comodel_name="purchase.order",
    )
    dst_purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Destination",
    )
    delete_source_po = fields.Boolean(
        string="Delete Source POs",
        default=False,
        help="Delete source POs after merge instead of just canceling them",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        purchase_orders = self.purchase_ids.browse(active_ids)
        self._check_all_values(purchase_orders)
        if (
            self.env.context.get("active_model") == "purchase.order"
            and len(active_ids) >= 1
        ):
            res["purchase_ids"] = [(6, 0, active_ids)]
            res["dst_purchase_id"] = self._get_ordered_purchase(active_ids)[-1].id
        return res

    # ----------------------------------------
    # Check method
    # ----------------------------------------

    def _check_all_values(self, purchase_orders):
        """Contain all check method"""
        self._check_state(purchase_orders)
        self._check_content(purchase_orders)

    def _check_state(self, purchase_orders):
        non_draft_po = purchase_orders.filtered(lambda p: p.state != "draft")
        if non_draft_po:
            po_names = non_draft_po.mapped("name")
            raise ValidationError(
                _(
                    "You can't merge purchase orders that "
                    "aren't in draft state like: {}"
                ).format(po_names)
            )

    def _check_content(self, purchase_orders):
        error_messages = []

        currencies = purchase_orders.currency_id
        if len(currencies) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different currencies: %s",
                    ", ".join(currencies.mapped("name")),
                )
            )
        picking_types = purchase_orders.picking_type_id
        if len(picking_types) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different picking types: %s",
                    ", ".join(picking_types.mapped("name")),
                )
            )

        incoterms = purchase_orders.incoterm_id
        if len(incoterms) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different incoterms: %s",
                    ", ".join(incoterms.mapped("name")),
                )
            )

        payment_terms = purchase_orders.payment_term_id
        if len(payment_terms) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different payment terms: %s",
                    ", ".join(payment_terms.mapped("name")),
                )
            )

        fiscal_positions = purchase_orders.fiscal_position_id
        if len(fiscal_positions) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders "
                    "with different fiscal positions: %s",
                    ", ".join(fiscal_positions.mapped("name")),
                )
            )

        suppliers = purchase_orders.partner_id
        if len(suppliers) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different suppliers: %s",
                    ", ".join(suppliers.mapped("name")),
                )
            )

        if error_messages:
            raise ValidationError("\n".join(error_messages))

    # ----------------------------------------
    # Update method
    # ----------------------------------------

    @api.model
    def _update_values(self, src_purchase, dst_purchase):
        """Update values of dst_purchase with the ones from the src_purchase.
        :param src_purchase : recordset of source purchase.order
        :param dst_purchase : record of destination purchase.order
        """
        # merge all order lines + set origin and partner_ref
        dst_purchase.write(self._get_update_values(src_purchase, dst_purchase))
        for po in src_purchase:
            self._add_message("to", [dst_purchase.name], po)

        po_names = src_purchase.mapped("name")
        self._add_message("from", po_names, dst_purchase)

    @api.model
    def _get_update_values(self, src_purchase, dst_purchase):
        """Generate values of dst_purchase with the ones from the src_purchase.
        :param src_purchase : recordset of source purchase.order
        :param dst_purchase : record of destination purchase.order
        """
        # initialize destination origin and partner_ref
        origin = {dst_purchase.origin or ""}
        origin.update({x.origin for x in src_purchase if x.origin})

        partner_ref = {dst_purchase.partner_ref or ""}
        partner_ref.update({x.partner_ref for x in src_purchase if x.partner_ref})

        # Generate destination origin and partner_ref
        src_order_line = src_purchase.mapped("order_line")

        # Copy order lines without triggering compute methods
        order_lines = [(4, line.id, 0) for line in src_order_line]

        return {
            "order_line": order_lines,
            "origin": ", ".join(origin),
            "partner_ref": ", ".join(partner_ref),
        }

    def _add_message(self, way, po_name, po):
        """Send a message post with to advise the po about the merge.
        :param way : choice between 'from' or 'to'
        :param po_name : list of purchase order name to add in the body
        :param po_name : the po where the message will be posted
        """
        subject = "Merge purchase order"
        body = _(
            "This purchase order lines have been merged %(way)s : %(po_names)s",
            way=way,
            po_names=" ,".join(po_name),
        )

        po.message_post(body=body, subject=subject)

    # ----------------------------------------
    # Reference reassignment
    # ----------------------------------------

    def _iter_concrete_models(self):
        """Yield every stored, non-transient model of the registry."""
        for model_name in self.env.registry:
            if model_name in MERGE_EXCLUDED_MODELS:
                continue
            model = self.env[model_name]
            if model._abstract or model._transient or not model._auto:
                continue
            yield model_name, model

    def _reassign_many2one_refs(self, src_purchase, dst_purchase):
        """Repoint every stored many2one aiming at a source PO to the target."""
        for model_name, model in self._iter_concrete_models():
            for field in model._fields.values():
                if (
                    field.type != "many2one"
                    or field.comodel_name != "purchase.order"
                    or not field.store
                    or field.related
                    or (field.compute and not field.inverse)
                ):
                    continue
                records = (
                    model.sudo()
                    .with_context(active_test=False)
                    .search([(field.name, "in", src_purchase.ids)])
                )
                if not records:
                    continue
                records.write({field.name: dst_purchase.id})
                _logger.debug(
                    "Merge PO: moved %s record(s) on %s.%s",
                    len(records),
                    model_name,
                    field.name,
                )

    def _reassign_generic_refs(self, src_purchase, dst_purchase):
        """Repoint generic ``res_model``/``res_id`` references.

        Covers ``mail.message``, ``mail.activity``, ``mail.followers``,
        ``ir.attachment`` and any other model using a ``Many2oneReference``.
        """
        for model_name, model in self._iter_concrete_models():
            for field in model._fields.values():
                if field.type != "many2one_reference" or not field.store:
                    continue
                model_field = field.model_field
                if not model_field or model_field not in model._fields:
                    continue
                records = (
                    model.sudo()
                    .with_context(active_test=False)
                    .search(
                        [
                            (model_field, "=", "purchase.order"),
                            (field.name, "in", src_purchase.ids),
                        ]
                    )
                )
                if not records:
                    continue
                if model_name == "mail.followers":
                    records = self._drop_duplicated_followers(
                        model, records, field.name, model_field, dst_purchase
                    )
                    if not records:
                        continue
                records.write({field.name: dst_purchase.id})
                _logger.debug(
                    "Merge PO: moved %s record(s) on %s.%s",
                    len(records),
                    model_name,
                    field.name,
                )

    def _drop_duplicated_followers(
        self, model, records, res_id_field, model_field, dst_purchase
    ):
        """Unlink source followers already following the destination PO.

        ``mail.followers`` has a unique constraint on
        (res_model, res_id, partner_id), so duplicates must be removed instead
        of moved.
        """
        existing = model.sudo().search(
            [
                (model_field, "=", "purchase.order"),
                (res_id_field, "=", dst_purchase.id),
                ("partner_id", "in", records.mapped("partner_id").ids),
            ]
        )
        duplicated = records.filtered(
            lambda f, partners=existing.mapped("partner_id"): f.partner_id in partners
        )
        duplicated.unlink()
        return records - duplicated

    def _reassign_reference_refs(self, src_purchase, dst_purchase):
        """Repoint stored ``Reference`` fields pointing at a source PO."""
        src_values = [f"purchase.order,{po_id}" for po_id in src_purchase.ids]
        dst_value = f"purchase.order,{dst_purchase.id}"
        for model_name, model in self._iter_concrete_models():
            for field in model._fields.values():
                if field.type != "reference" or not field.store or field.related:
                    continue
                records = (
                    model.sudo()
                    .with_context(active_test=False)
                    .search([(field.name, "in", src_values)])
                )
                if not records:
                    continue
                records.write({field.name: dst_value})
                _logger.debug(
                    "Merge PO: moved %s record(s) on %s.%s",
                    len(records),
                    model_name,
                    field.name,
                )

    def _reassign_references(self, src_purchase, dst_purchase):
        """Move every reference to the source POs onto the destination PO."""
        self._reassign_generic_refs(src_purchase, dst_purchase)
        self._reassign_many2one_refs(src_purchase, dst_purchase)
        self._reassign_reference_refs(src_purchase, dst_purchase)

    # ----------------------------------------
    # Merge
    # ----------------------------------------

    def _merge(self, purchases, dst_purchase=None):
        """private implementation of merge purchase
        :param purchases : ids of purchase to merge
        :param dst_purchase : record of destination purchase.order
        """
        if len(purchases) < 2:
            return
        self._check_all_values(purchases)

        # Determine source and destination purchases
        if dst_purchase and dst_purchase in purchases:
            src_purchase = purchases - dst_purchase
        else:
            dst_purchase = self._get_ordered_purchase(purchases.ids)[-1]
            src_purchase = purchases - dst_purchase

        # Move everything pointing at the source POs (messages, activities,
        # followers, attachments, related documents...). Done before
        # ``_update_values`` so the merge notes posted below stay in place.
        self._reassign_references(src_purchase, dst_purchase)

        # Move order lines and concatenate origin / partner_ref
        self._update_values(src_purchase, dst_purchase)

        # delete or cancel source purchase, since they are merged
        if self.delete_source_po:
            src_purchase.unlink()
        else:
            src_purchase.button_cancel()

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    @api.model
    def _get_ordered_purchase(self, purchase_ids):
        """Helper returns a `purchase.order` recordset ordered by create_date

        Newest first, so ``[-1]`` is the oldest purchase order, which is the
        one used as merge destination by default. ``id`` is used as tie
        breaker because purchase orders created in the same transaction share
        the very same ``create_date``.

        :param purchase_ids : list of purchase ids to sort
        """
        return (
            self.env["purchase.order"]
            .browse(purchase_ids)
            .sorted(
                key=lambda p: (p.create_date or "", p.id),
                reverse=True,
            )
        )

    # ----------------------------------------
    # Actions
    # ----------------------------------------

    def action_merge(self):
        """Merge Quotation button. Merge the selected purchases."""
        if not self.purchase_ids:
            return False
        self._merge(self.purchase_ids, self.dst_purchase_id)
        return True
