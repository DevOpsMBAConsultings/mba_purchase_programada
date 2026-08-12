# MBA Purchase Order Format (`mba_purchase_order_format`)

Formato personalizado del reporte PDF de Orden de Compra, con identidad corporativa en azul y rojo.

## Qué hace

Reemplaza el diseño del reporte estándar de orden de compra de Odoo por uno con la imagen corporativa del cliente: encabezados más grandes para Proveedor y Número de Orden, mejor separación entre el logo y los datos del documento, y visualización forzada de teléfono/correo del proveedor.

## Cómo funciona

Es un módulo puramente de presentación: no agrega modelos ni lógica de negocio en Python. Todo el cambio vive en `views/report_purchaseorder.xml`, una vista QWeb que **hereda** el reporte nativo de compras (`purchase.report_purchaseorder`) y sobreescribe fragmentos puntuales de su plantilla (vía XPath) para cambiar estilos y reordenar campos, sin tocar el reporte original.

## Dependencias

- `purchase`

## Licencia

LGPL-3.
