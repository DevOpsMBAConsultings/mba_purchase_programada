{
    'name': 'MBA - Compras Programadas (MBA Consultings)',
    'version': '18.0.1.0.11',
    'category': 'Purchases',
    'summary': 'Órdenes de compra mensuales/recurrentes por proveedor, con selección manual de sus productos configurados',
    'description': """
Compras Programadas
====================
Agrega un menú "Compras Programadas" en Compras > Órdenes para generar
órdenes de compra recurrentes (mensuales) a un proveedor.

Al elegir el proveedor, el botón "Cargar productos del proveedor" abre una
pantalla con todos los productos que lo tienen configurado en la pestaña
"Compras" de su ficha (product.supplierinfo), sin necesidad de marcar nada:
el comprador escribe la cantidad únicamente en los que quiere pedir este
mes, y al presionar "Agregar productos" solo esos (cantidad > 0) se agregan
a la orden.

Estas órdenes usan el mismo modelo y el mismo flujo que las órdenes de
compra normales (purchase.order), incluido el mismo consecutivo de
numeración; solo se agrega un campo "Tipo de orden" (Transaccional /
Programada) para poder distinguirlas y filtrarlas en reportes.
    """,
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': ['purchase', 'purchase_stock', 'stock', 'mb_stock_orderpoint_vendor'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_programada_line_views.xml',
        'views/purchase_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mba_purchase_programada/static/src/scss/purchase_programada.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
