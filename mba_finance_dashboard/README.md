# Finance Overview Dashboard (`mba_finance_dashboard`)

Tablero financiero que se instala **ya armado**. El usuario entra a Tableros y
ve el estado del negocio, sin configurar nada.

## Qué muestra

- **Antigüedad de cuentas por cobrar** por tramo de días vencidos, con monto y
  porcentaje sobre el total.
- **Antigüedad de cuentas por pagar**, misma estructura.
- **Posición**: por cobrar contra por pagar, posición neta, cobertura, y cuánto
  del saldo está efectivamente vencido.
- **Estado de resultados del año**: ingresos, costo de ventas, utilidad bruta,
  gastos operativos y resultado neto, con margen sobre ventas.
- **Top 10 clientes y proveedores con saldo vencido**.

Todo con datos en vivo: cada vez que se abre el tablero, las cifras se
recalculan contra la base.

## Instalación

Instale el módulo. El tablero aparece en **Tableros → Finance → Finance
Overview**.

Los tramos de antigüedad salen de la configuración de la compañía, que se
ajusta en Contabilidad → Ajustes → Aged Balance. Si cambia los umbrales, el
tablero se actualiza solo: las etiquetas se leen de la misma configuración.

## Dependencias

- [`mba_account_aging`](../mba_account_aging) — provee el modelo de antigüedad.
- `spreadsheet_dashboard`, `spreadsheet_account` — ambos en Odoo Community.

## Personalización

El tablero es una hoja de cálculo de Odoo. Se edita desde la interfaz sin tocar
código: agregar bloques, cambiar textos, reordenar. El archivo de origen está en
`data/files/finance_dashboard.osheet.json` si prefiere versionar los cambios.

## Licencia

LGPL-3.
