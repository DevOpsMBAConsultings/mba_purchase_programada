# Purchase Order Consolidation (`mba_purchase_consolidation`)

Wizard para consolidar varias órdenes de compra en borrador del mismo proveedor en una sola orden, con opción de eliminar las órdenes originales.

## Qué hace

- Permite seleccionar varias órdenes de compra en borrador y fusionarlas en una orden de destino.
- Mueve las líneas de las órdenes origen a la orden destino.
- Opción de **eliminar** las órdenes origen tras la fusión, en vez de solo cancelarlas (comportamiento configurable con `delete_source_po`).

## Cómo funciona

Es una adaptación del wizard `purchase_order_merge` del ecosistema OCA/Camptocamp (ver cabecera de licencia en el código: Copyright 2022 Camptocamp SA, adaptado 2026 por MBA Consultings).

El wizard (`purchase.merge.automatic.wizard`) recibe las órdenes seleccionadas por el usuario:

1. Valida que sean compatibles entre sí (mismo proveedor, misma compañía, mismo estado, etc.) — si no lo son, lanza un `ValidationError` explicando por qué.
2. El usuario elige cuál orden es el destino (`dst_purchase_id`).
3. El wizard mueve las líneas de compra de las órdenes origen hacia la orden destino y reasigna las referencias que apuntaban a esas órdenes (excluyendo explícitamente `purchase.order.line`, que se mueve aparte, e `ir.model.data`, que nunca se toca).
4. Según la opción elegida, las órdenes origen quedan canceladas o se eliminan.

Incluye tests (`tests/test_purchase_merge.py`) que cubren el flujo de fusión.

## Dependencias

- `purchase`

## Licencia

AGPL-3.
