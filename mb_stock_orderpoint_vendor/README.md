# MBA - Proveedor en Reabastecimiento de Inventario (MBA Consultings)

Módulo de **Odoo 18.0 CE** diseñado por **MBA Consultings** que personaliza el comportamiento de la columna **Proveedor** (`vendor_id`) en las reglas y órdenes de reabastecimiento de inventario (`stock.warehouse.orderpoint`).

---

## 🎯 Objetivo y Funcionalidades
1. **Asignación automática del primer proveedor del producto:**
   * Al seleccionar o evaluar un producto en una regla de reabastecimiento, si dicho producto tiene proveedores definidos en la pestaña de **Compras** (`product.product -> seller_ids`), se asigna de manera automática el **primer proveedor** de la lista (`seller_ids[0].partner_id`).
   * Cumple con los estándares multi-compañía de Odoo 18, filtrando los proveedores compatibles con la compañía de la orden de reabastecimiento.
2. **Menú desplegable restringido por producto (Domain seguro):**
   * Al hacer clic para modificar el campo **Proveedor** en la vista de lista editable o formulario de reabastecimiento, el menú desplegable sólo muestra los proveedores configurados en la pestaña de **Compras** de ese producto en particular (`allowed_vendor_ids`).
   * Evita la creación en caliente (`no_create`, `no_create_edit`) para garantizar que todos los proveedores del producto se gestionen primero en su ficha de compra.
3. **Columna "Producto" separada en Referencia / Descripción (18.0.1.0.5):**
   * La lista de Reabastecimiento mostraba una sola columna `product_id` con el `display_name` combinado (`[REF] Nombre`), sin forma de ordenar/filtrar solo por referencia.
   * Se agregó el campo relacionado `mba_reference` (`product_id.default_code`, `store=True`) como columna **Referencia** independiente, insertada antes de `product_id`.
   * Al campo `product_id` se le agregó `display_default_code: False` en su `context` (clave estándar de Odoo, usada en 20+ lugares del core para el mismo propósito) para que deje de repetir el prefijo `[REF]` y solo muestre la descripción; se le cambió el `string` a "Descripción".
   * Se descartó la sintaxis de "campo con punto" (`<field name="product_id.default_code"/>`) directamente en la vista: se verificó contra el código fuente de Odoo (búsqueda en `odoo/odoo` en GitHub) que ese patrón no se usa en ningún lado del core como columna de solo lectura, por lo que no es una funcionalidad soportada — se usó en su lugar un campo `related` real, el mismo patrón ya probado en este módulo para `mba_sold_m1..m4`.
4. **Columna "Por ordenar" junto a Descripción (18.0.1.0.6):**
   * El campo core `qty_to_order` (cantidad sugerida a pedir, editable por el usuario antes de presionar "Orden") ya existía en la vista pero al final, después de Mínimo/Máximo/UdM, obligando a hacer scroll horizontal para verla junto al producto.
   * Se reubicó con `position="move"` (no se duplica el campo, se reubica el nodo existente del arch core) justo después de `product_id`, para que Referencia, Descripción, Por ordenar y el histórico de ventas queden visibles juntos.
5. **"A la mano" e historial de ventas en la Orden de Compra (18.0.1.0.7):**
   * El comprador pedía tener, al agregar un producto en Compras > Órdenes > Órdenes de compra > Nuevo, el mismo contexto que ya existe en Reabastecimiento: cuánto hay a la mano y cómo se ha movido el producto en los últimos 4 meses, sin salir de la orden.
   * Se agregó `mba_qty_on_hand` en `purchase.order.line` (modelo nuevo, `models/purchase_order_line.py`): campo **computado, no almacenado**, que llama a `product_id.with_context(warehouse=...).qty_available` usando el almacén de recepción de la orden (`order_id.picking_type_id.warehouse_id`). No se guarda porque el almacén puede cambiar mientras la orden está en borrador. Si la orden no tiene almacén definido o el producto no maneja inventario, muestra `0`.
   * Se agregaron `mba_sold_m1..m4` y `mba_sold_total_4m` en `purchase.order.line` como campos `related` a `product_id.product_tmpl_id`, mismo patrón ya usado en `stock_warehouse_orderpoint.py` — el cálculo real (ventana móvil de 4 meses, datos de Sage) sigue viviendo únicamente en `product_template.py`, no se duplica lógica.
   * Vista nueva (`views/purchase_order_line_views.xml`): hereda `purchase.purchase_order_form` y ancla el xpath en `field[@name='order_line']//field[@name='product_id']` (no en el tag `<list>`/`<tree>` del core, para no depender de su sintaxis) e inserta las columnas "A la mano", M(-1)..M(-4) y Total 4M justo después de Producto, todas de solo lectura y `optional="show"` (ocultables desde el ⚙️ de la lista, igual que en Reabastecimiento).

---

## 🏗️ Estructura Técnica
```
mb_stock_orderpoint_vendor/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── mba_product_sales_history.py
│   ├── product_template.py
│   ├── purchase_order_line.py
│   └── stock_warehouse_orderpoint.py
├── views/
│   ├── stock_warehouse_orderpoint_views.xml
│   └── purchase_order_line_views.xml
└── README.md
```

---

## 📜 Estándares y Cumplimiento (`AGENTS.md`)
*   **Prefijo del Módulo:** `mb_stock_orderpoint_vendor`
*   **Autor:** `"MBA Consultings, Brooks González"`
*   **Nombre Técnico en Manifiesto:** `"MBA - Proveedor en Reabastecimiento de Inventario (MBA Consultings)"`
*   **XPath Semánticos:** Vistas heredadas usando atributos estables y únicos (`//field[@name='vendor_id']`, `//field[@name='product_id']`) evitando selectores posicionales frágiles.
