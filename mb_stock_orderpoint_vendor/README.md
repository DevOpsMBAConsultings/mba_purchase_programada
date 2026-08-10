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

---

## 🏗️ Estructura Técnica
```
mb_stock_orderpoint_vendor/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── stock_warehouse_orderpoint.py
├── views/
│   └── stock_warehouse_orderpoint_views.xml
└── README.md
```

---

## 📜 Estándares y Cumplimiento (`rules.md`)
*   **Prefijo del Módulo:** `mb_stock_orderpoint_vendor`
*   **Autor:** `"MBA Consultings, Brooks González"`
*   **Nombre Técnico en Manifiesto:** `"MBA - Proveedor en Reabastecimiento de Inventario (MBA Consultings)"`
*   **XPath Semánticos:** Vistas heredadas usando atributos estables y únicos (`//field[@name='vendor_id']`, `//field[@name='product_id']`) evitando selectores posicionales frágiles.
