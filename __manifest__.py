# Copyright 2026 MBA Consultings
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase Order Consolidation",
    "version": "18.0.1.0.0",
    "category": "Purchases",
    "license": "LGPL-3",
    "author": "MBA Consultings",
    "website": "https://www.mbaconsultings.com",
    "depends": [
        "purchase",
        "openupgrade",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_merge_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
}
