{
    "name": "Product Multi Pricelist Display",
    "version": "18.0.1.0.1",
    "category": "Sales",
    "depends": ["product", "sale"],
    "data": [
        "views/pricelist_views.xml",
        "views/product_views.xml",
    ],
    "author": "MBA Consultings",
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "summary": "Muestra precios de múltiples tarifas como columnas dinámicas en la vista de lista de productos.",
    "description": """
        Módulo de visualización de múltiples listas de precios / tarifas en Odoo 18.

        Funcionalidades principales:
        1. Configuración por Tarifa: Añade el campo 'Mostrar en lista de productos' (display_in_product_list) en las tarifas (product.pricelist).
        2. Inyección Dinámica de Columnas: Muestra columnas personalizadas en la vista lista/árbol de productos (product.template y product.product) para cada tarifa marcada.
        3. Cálculo de Precios en Tiempo Real: Sobrescribe los métodos ORM (get_view, fields_get, read, web_search_read) para obtener el precio preciso por tarifa para cada variante o plantilla.
        4. Limpieza de Caché de Vistas: Invalida automáticamente la caché de vistas (ir.ui.view.clear_caches()) al activar o desactivar una tarifa para que la UI se actualice de inmediato.
    """,
}
