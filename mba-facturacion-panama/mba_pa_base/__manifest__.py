{
    "name": "Panamá - Catálogos Base (MBA)",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Catálogos base de la DGI y modificaciones a Contactos para Panamá.",
    "author": "MBA Consultings",
    "website": "https://www.mbaconsultings.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/dgi.provincia.csv",
        "data/dgi.distrito.csv",
        "data/dgi.corregimiento.csv",
        "views/res_partner_views.xml",
        "views/res_company_views.xml"
    ],
    "installable": True,
    "application": False,
}
