# Formato Cotización (`formato_cotizacion_simplificat`)

Plantilla base reutilizable para el reporte PDF de cotizaciones y pedidos de venta.

## Qué hace

Sobreescribe el reporte estándar de cotización/pedido de venta (`report_saleorder`) de Odoo con un diseño propio: logos, tipografías y colores corporativos inyectados automáticamente, sin referencias fijas ("hardcoded") a un cliente en particular — pensado como plantilla base reutilizable en otros proyectos.

## Cómo funciona

Es un módulo puramente de presentación, sin modelos Python. Todo el cambio vive en `views/report_saleorder.xml`, que hereda el reporte nativo de ventas y lo sobreescribe vía XPath para cambiar el layout, agregar la identidad visual y limpiar elementos del reporte estándar que no aplican.

## Dependencias

- `sale`

## Licencia

LGPL-3.
