# MBA - Disponibilidad de Producto en Cotización (MBA Consultings)

Módulo para Odoo 18.0 CE que añade la columna de disponibilidad de inventario (`Stock Disp.`) en las líneas de pedido de venta antes de la Unidad de Medida (UdM).

## Funcionalidades principales

1. **Columna Stock Disponible (`free_qty_available`)**:
   - Muestra las unidades disponibles libres de inventario por producto considerando el almacén (`warehouse_id`) de la cotización.
   - Posicionada antes de la columna `UdM` (`product_uom`) en la tabla de líneas de la cotización.

## Autor y Licencia
- **Autor**: MBA Consultings
- **Licencia**: LGPL-3
