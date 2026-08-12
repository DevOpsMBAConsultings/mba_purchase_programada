# -*- coding: utf-8 -*-
{
    'name': 'MBA Purchase Subtotal Adjust',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Recalcula automáticamente el precio unitario al modificar el subtotal en órdenes de compra (MBA Consultings)',
    'author': 'MBA Consultings',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
