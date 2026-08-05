# -*- coding: utf-8 -*-
{
    'name': 'MBA - Proveedor en Reabastecimiento de Inventario (MBA Consultings)',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Asignación automática y filtrado de proveedor en reglas de reabastecimiento según la pestaña de compras del producto.',
    'description': """
MBA - Proveedor en Reabastecimiento de Inventario
=================================================
Este módulo personaliza el comportamiento de la columna Proveedor en el Reabastecimiento de Inventario (stock.warehouse.orderpoint) para Odoo 18.0 CE:
- Asigna automáticamente como proveedor por defecto el primero configurado en la pestaña de Compras del producto.
- Restringe el menú desplegable (domain) del campo Proveedor exclusivamente a los proveedores configurados para el producto seleccionado.
    """,
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'purchase_stock',
    ],
    'data': [
        'views/stock_warehouse_orderpoint_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
