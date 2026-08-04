# Sale Line Pricelist (MBA Consultings)

Módulo para Odoo 18 CE que permite la selección individual de listas de precios (tarifas) por cada línea de pedido de venta / cotización (`sale.order.line`).

## Funcionalidades principales

1. **Tarifa por línea (`line_pricelist_id`)**:
   - Cada línea de cotización dispone de un campo desplegable para seleccionar la tarifa deseada.
   - El precio unitario de la línea se recarga automáticamente al cambiar la tarifa.

2. **Visualización de Precios en Paréntesis**:
   - Al desplegar las opciones en el campo *Pricelist* de cada línea, se muestra el nombre de la tarifa y entre paréntesis el precio calculado para dicho producto y cantidad:
     `Nombre de Tarifa (Precio Símbolo)` por ejemplo `Detal (PAB) (6.10 B/.)`.
   - Permite al usuario conocer de antemano el precio unitario con cada tarifa antes de elegirla.

3. **Ocultación de la Tarifa Global**:
   - Oculta el campo `pricelist_id` en la cabecera del pedido de venta para priorizar la asignación a nivel de línea.

4. **Nota Interna de Proveedor (`internal_vendor_note`)**:
   - Añade una columna `Vendor` en la tabla de líneas de venta.

## Autor y Licencia
- **Autor**: MBA Consultings, Brooks Gonzalez
- **Licencia**: LGPL-3
