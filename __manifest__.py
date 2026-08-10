{
    'name': 'MBA - Compras Programadas (MBA Consultings)',
    'version': '18.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Órdenes de compra mensuales/recurrentes por proveedor, con carga automática de sus productos configurados',
    'description': """
Compras Programadas
====================
Agrega un menú "Compras Programadas" en Compras > Órdenes para generar
órdenes de compra recurrentes (mensuales) a un proveedor.

Al seleccionar el proveedor, se cargan automáticamente todas las líneas de
producto que lo tengan configurado en la pestaña "Compras" de la ficha del
producto (Proveedores del producto / product.supplierinfo), con cantidad en
cero para que el comprador la complete.

Estas órdenes usan el mismo modelo y el mismo flujo que las órdenes de
compra normales (purchase.order); solo se agrega un campo "Tipo de orden"
(Transaccional / Programada) para poder distinguirlas y filtrarlas en
reportes.
    """,
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
