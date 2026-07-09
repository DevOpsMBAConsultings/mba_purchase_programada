{
    "name": "Panamá - Conector The Factory HKA (MBA)",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Conector API REST para el PAC The Factory HKA en Panamá.",
    "author": "MBA Consultings",
    "website": "https://www.mbaconsultings.com",
    "license": "LGPL-3",
    "depends": [
        "mba_pa_edi",
        "mba_pa_sale"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/account_move_views.xml",
        "wizard/hka_anular_factura_wizard_views.xml"
    ],
    "installable": True,
    "application": False,
}
