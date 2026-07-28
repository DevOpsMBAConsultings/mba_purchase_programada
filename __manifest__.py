# Copyright 2022 Camptocamp SA
# Copyright 2026 MBA Consultings
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Purchase Order Consolidation (MBA Consultings)",
    "summary": "Consolidate purchase orders by supplier with delete option",
    "version": "18.0.1.0.0",
    "author": "MBA Consultings, Brooks Gonzalez",
    "website": "https://www.mbaconsultings.com",
    "license": "LGPL-3",
    "category": "Purchase",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_merge_views.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
