# -*- coding: utf-8 -*-
{
    'name': 'MBA - Proveedor en Reabastecimiento de Inventario (MBA Consultings)',
    'version': '18.0.1.0.8',
    'category': 'Inventory/Inventory',
    'summary': 'Asignación automática y filtrado de proveedor en reglas de reabastecimiento según la pestaña de compras del producto.',
    'description': """
MBA - Proveedor y Historial de Ventas en Reabastecimiento de Inventario
=======================================================================
Este módulo personaliza el comportamiento del Reabastecimiento de Inventario
(stock.warehouse.orderpoint) para Odoo 18.0 CE:

- Asigna automáticamente el proveedor principal del producto.
- Restringe el selector de proveedor a los configurados en el producto.
- Muestra columnas opcionales con el historial de ventas de los últimos 4 meses
  (rolling window automático: M-4, M-3, M-2, M-1, Total 4M).
- Los datos históricos se importan desde Sage; a futuro se calculan desde Odoo.
- Separa la columna combinada "Producto" en dos columnas: Referencia
  (product_id.default_code, campo relacionado propio) y Descripción
  (product_id sin el prefijo de referencia, vía context display_default_code=False).
- Reubica la columna core "Por ordenar" (qty_to_order) junto a Descripción,
  para ver de un vistazo cuánto hay y cuánto se sugiere pedir.
- Repite las mismas columnas de existencia e historial de ventas
  ("A la mano", M(-1)..M(-4), Total 4M) en las líneas de la Orden de
  Compra (Compras > Órdenes > Órdenes de compra), para que el comprador
  tenga el mismo contexto al momento de decidir cuánto pedir.
- Reubica Cantidad y Precio unitario junto a Descripción (antes del
  historial de ventas), y Subtotal justo después, para no tener que
  hacer scroll horizontal para ver el precio.
    """,
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://www.mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'purchase_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/server_action.xml',
        'views/stock_warehouse_orderpoint_views.xml',
        'views/purchase_order_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
