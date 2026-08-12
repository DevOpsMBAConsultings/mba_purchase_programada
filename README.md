# Product Multi Pricelist Display (`product_multi_pricelist_display`)

Muestra el precio de varias listas de precios como columnas en la vista de lista de productos, en vez de tener que abrir cada lista por separado para comparar precios.

## Qué hace

- Agrega un checkbox **"Mostrar en lista de productos"** en cada lista de precios (`product.pricelist`).
- Las listas marcadas aparecen como columnas adicionales (opcionales, se pueden ocultar) en la vista de lista de `product.template` y `product.product`, junto a la cantidad disponible en inventario.

## Cómo funciona

No usa campos `store=True` en la base de datos — los precios se calculan **al vuelo** cada vez que se pide la vista:

1. `get_view()` intercepta la construcción de la vista de lista y, por cada lista de precios marcada con `display_in_product_list`, inyecta dinámicamente un campo virtual `price_pricelist_<id>` en el XML de la vista (arch), justo junto al precio de venta.
2. `fields_get()` declara esos campos virtuales como campos `float` de solo lectura, para que Odoo los reconozca aunque no existan en la base de datos.
3. `read()` y `web_search_read()` interceptan la lectura de esos campos y calculan el precio real llamando a `pricelist._get_product_price()` para cada producto, en el momento en que la vista los pide.

Cuando se activa o desactiva una lista desde su checkbox, se limpia el caché de vistas (`ir.ui.view.clear_caches()`) para que las columnas se actualicen de inmediato sin reiniciar Odoo.

## Dependencias

- `product`, `sale`, `stock`

## Licencia

AGPL-3.
