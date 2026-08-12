# -*- coding: utf-8 -*-
{
    'name': 'MBA Vendor Bill Subtotal Adjust',
    'version': '18.0.1.0.1',
    'category': 'Accounting/Accounting',
    'summary': 'Recalcula automáticamente el precio unitario al modificar el subtotal en facturas de proveedor (MBA Consultings)',
    'author': 'MBA Consultings',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
