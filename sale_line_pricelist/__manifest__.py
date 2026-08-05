{
    "name": "Sale Line Pricelist (MBA Consultings)",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Selección de lista de precios por línea de cotización con precio calculado visible en paréntesis.",
    "description": """
        Módulo de selección de Tarifas / Listas de Precios por línea de venta en Odoo 18.

        Funcionalidades principales:
        1. Selección de Tarifa por Línea: Permite seleccionar una lista de precios específica (line_pricelist_id) para cada producto en la cotización/pedido de venta.
        2. Muestra de Precios en Paréntesis: Al desplegar la lista de tarifas en cada línea, muestra el nombre de la tarifa junto con el precio calculado para ese producto y cantidad entre paréntesis (ej. 'Detal (PAB) (6.10 B/.)').
        3. Ocultamiento de Tarifa Global: Oculta el campo de tarifa global en la cabecera de la cotización para dar prioridad al cálculo por línea.
        4. Campo Nota de Proveedor: Añade el campo de nota interna de proveedor (internal_vendor_note) en las líneas de la orden.
    """,
    "author": "MBA Consultings, Brooks Gonzalez",
    "website": "https://www.mbaconsultings.com",
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
