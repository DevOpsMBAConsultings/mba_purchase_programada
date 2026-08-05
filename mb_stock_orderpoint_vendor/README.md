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
