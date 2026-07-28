# Copyright 2026 MBA Consultings
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseMerge(TransactionCase):
    """Test purchase order consolidation wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["purchase.merge.automatic.wizard"]
        cls.po_model = cls.env["purchase.order"]
        cls.partner_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]

        # Create test supplier
        cls.supplier = cls.partner_model.create({
            "name": "Test Supplier",
            "is_company": True,
        })

        # Create test products
        cls.product_a = cls.product_model.create({
            "name": "Product A",
            "type": "product",
            "default_code": "PA",
        })
        cls.product_b = cls.product_model.create({
            "name": "Product B",
            "type": "product",
            "default_code": "PB",
        })

    def test_merge_two_draft_pos_same_supplier(self):
        """Test merging two draft POs from the same supplier."""
        # Create first PO
        po1 = self.po_model.create({
            "partner_id": self.supplier.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product_a.id,
                    "product_qty": 10,
                    "product_uom_id": self.product_a.uom_id.id,
                    "price_unit": 100,
                }),
            ],
        })

        # Create second PO
        po2 = self.po_model.create({
            "partner_id": self.supplier.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product_b.id,
                    "product_qty": 20,
                    "product_uom_id": self.product_b.uom_id.id,
                    "price_unit": 50,
                }),
            ],
        })

        # Merge POs
        wizard = self.wizard_model.create({
            "purchase_ids": [(6, 0, [po1.id, po2.id])],
            "dst_purchase_id": po1.id,
            "delete_source_po": False,
        })
        wizard.action_merge()

        # Verify: po1 should have 2 lines, po2 should be cancelled
        self.assertEqual(len(po1.order_line), 2, "Destination PO should have 2 lines")
        self.assertEqual(po2.state, "cancel", "Source PO should be cancelled")

    def test_merge_different_suppliers_raises_error(self):
        """Test that merging POs from different suppliers raises an error."""
        supplier2 = self.partner_model.create({
            "name": "Test Supplier 2",
            "is_company": True,
        })

        po1 = self.po_model.create({
            "partner_id": self.supplier.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product_a.id,
                    "product_qty": 10,
                    "product_uom_id": self.product_a.uom_id.id,
                    "price_unit": 100,
                }),
            ],
        })

        po2 = self.po_model.create({
            "partner_id": supplier2.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product_b.id,
                    "product_qty": 20,
                    "product_uom_id": self.product_b.uom_id.id,
                    "price_unit": 50,
                }),
            ],
        })

        # Attempting merge should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            wizard = self.wizard_model.create({
                "purchase_ids": [(6, 0, [po1.id, po2.id])],
                "dst_purchase_id": po1.id,
            })
            wizard.action_merge()

        self.assertIn("different suppliers", str(cm.exception).lower())

    def test_merge_non_draft_po_raises_error(self):
        """Test that merging non-draft POs raises an error."""
        po1 = self.po_model.create({
            "partner_id": self.supplier.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product_a.id,
                    "product_qty": 10,
                    "product_uom_id": self.product_a.uom_id.id,
                    "price_unit": 100,
                }),
            ],
        })

        po2 = self.po_model.create({
            "partner_id": self.supplier.id,
            "order_line": [
                (0, 0, {
                    "product_id": self.product_b.id,
                    "product_qty": 20,
                    "product_uom_id": self.product_b.uom_id.id,
                    "price_unit": 50,
                }),
            ],
        })

        # Confirm po2 (change state from draft)
        po2.button_confirm()

        # Attempting merge should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            wizard = self.wizard_model.create({
                "purchase_ids": [(6, 0, [po1.id, po2.id])],
                "dst_purchase_id": po1.id,
            })
            wizard.action_merge()

        self.assertIn("draft", str(cm.exception).lower())
