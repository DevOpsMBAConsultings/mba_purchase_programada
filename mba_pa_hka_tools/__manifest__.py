# -*- coding: utf-8 -*-
{
    'name': 'MBA - HKA Tools Importador (MBA Consultings)',
    'version': '18.0.1.0.4',
    'category': 'Accounting/Localizations',
    'summary': 'Utilidades para descargar e importar facturas electrónicas desde HKA por CUFE.',
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://mbaconsultings.com',
    'depends': ['account', 'mba_pa_edi_hka'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hka_import_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
