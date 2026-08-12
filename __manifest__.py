{
    "name": "MBA - Disponibilidad de Producto en Cotización (MBA Consultings)",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Muestra las unidades disponibles en inventario como una columna en las líneas de la cotización.",
    "description": """
        Módulo de Disponibilidad de Producto en Cotizaciones para Odoo 18.0 CE.

        Funcionalidades principales:
        1. Campo de Disponibilidad: Añade el campo free_qty_available en sale.order.line.
        2. Columna en Cotización: Muestra la columna Stock Disp. en las líneas de pedido de venta antes de la columna UdM.
        3. Filtrado por Almacén: Calcula automáticamente las unidades libres de inventario considerando el almacén asignado a la cotización.
    """,
    "author": "MBA Consultings, Brooks González",
    "website": "https://www.mbaconsultings.com",
    "license": "LGPL-3",
    "depends": ["sale", "sale_stock"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
