{
    'name': 'MBA - Compras Programadas (MBA Consultings)',
    'version': '18.0.1.0.1',
    'category': 'Purchases',
    'summary': 'Órdenes de compra mensuales/recurrentes por proveedor, con selección manual de sus productos configurados',
    'description': """
Compras Programadas
====================
Agrega un menú "Compras Programadas" en Compras > Órdenes para generar
órdenes de compra recurrentes (mensuales) a un proveedor.

Al elegir el proveedor, el botón "Cargar productos del proveedor" abre una
lista con todos los productos que lo tienen configurado en la pestaña
"Compras" de su ficha (product.supplierinfo). El comprador marca los que
quiere pedir este mes, define la cantidad ahí mismo, y solo esos se agregan
a la orden -- mismo patrón de selección que Reabastecimiento en Inventario
(checkboxes + botón de acción masiva).

Estas órdenes usan el mismo modelo y el mismo flujo que las órdenes de
compra normales (purchase.order), incluido el mismo consecutivo de
numeración; solo se agrega un campo "Tipo de orden" (Transaccional /
Programada) para poder distinguirlas y filtrarlas en reportes.
    """,
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': ['purchase', 'purchase_stock', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_programada_line_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
