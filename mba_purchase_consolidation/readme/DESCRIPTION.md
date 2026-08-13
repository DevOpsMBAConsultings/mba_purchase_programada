Consolida varias solicitudes de cotización (RFQ) del mismo proveedor en una
sola, desde la vista de lista de órdenes de compra.

**Origen del código.** Este módulo es una adaptación de `purchase_merge`, cuyo
código fuente original pertenece a **Camptocamp SA** y se distribuye a través de
la **Odoo Community Association (OCA)** bajo licencia AGPL-3. MBA Consultings lo
modificó para adaptarlo a las necesidades de sus clientes y para hacerlo
compatible con Odoo 18.0. Se mantiene la misma licencia AGPL-3.

## Qué hace

Un asistente que se invoca desde el menú Acciones de la vista de lista de
órdenes de compra. Si se cumplen los criterios de fusión, todas las líneas de
las órdenes seleccionadas se transfieren a la orden destino, y campos como
`origin` y `partner_ref` se concatenan. Se registra un mensaje en el chatter de
cada orden indicando cuándo ocurrió la fusión y qué órdenes estuvieron
involucradas. Las órdenes de origen quedan canceladas, o eliminadas si así se
indica.

## Criterios de fusión

Todas las órdenes seleccionadas deben compartir:

- Proveedor
- Estado borrador
- Moneda
- Tipo de operación (picking type)
- Incoterm
- Términos de pago
- Posición fiscal

## Cambios respecto al módulo original

- **Opción de eliminar las órdenes de origen** en lugar de solo cancelarlas.
- **Compatibilidad con Odoo 18.0**: vistas migradas de `tree` a `list`.
- **Sin dependencia de `openupgradelib`**: la reasignación de referencias
  (mensajes, actividades, seguidores, adjuntos y documentos relacionados) se
  hace con el ORM nativo, porque la librería es incompatible con Odoo 18 al
  depender del modelo `ir.property`, eliminado en esta versión.
