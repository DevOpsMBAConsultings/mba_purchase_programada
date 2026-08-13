# Aged Balance Analysis (`mba_account_aging`)

Antigüedad de cuentas por cobrar y por pagar **por días vencidos**, expuesta
como un modelo analizable que se puede pivotar, graficar, filtrar y — lo más
importante — insertar en tableros y hojas de cálculo.

## El problema que resuelve

Odoo 18 Community no trae los tramos de antigüedad (0-30 / 31-60 / 61-90 / +90)
como un dato consultable. Existen reportes tipo asistente que generan un PDF,
pero ese resultado no se puede llevar a un tablero ni cruzar con otros datos.

Un campo calculado tampoco sirve: la antigüedad cambia todos los días, así que
un valor almacenado queda obsoleto a la mañana siguiente y obliga a programar
recálculos.

Este módulo usa una **vista SQL**. Los tramos se calculan contra `CURRENT_DATE`
en cada consulta: siempre están al día, no ocupan espacio y no requieren tareas
programadas.

## Características

- Tramos calculados sobre la **fecha de vencimiento** del apunte, no sobre el
  término de pago del cliente.
- **Tramos configurables por compañía** (Contabilidad → Ajustes → Aged Balance).
  Por defecto 30 / 60 / 90 días; una compañía que trabaja a 45 días los ajusta
  sin tocar código. En bases multicompañía cada una usa los suyos.
- Un solo modelo cubre clientes y proveedores, distinguidos por el campo
  *Ledger*. Los saldos por pagar se exponen en positivo para que sumen de
  forma natural.
- Vistas pivote, gráfico de pastel y lista, con filtros por tramo, libro,
  vendedor, diario y empresa matriz.
- Solo lectura, con permisos para los tres grupos contables estándar.
- Sin dependencias de Odoo Enterprise.

## Campos disponibles

| Campo | Descripción |
| --- | --- |
| `ledger` | Receivable / Payable |
| `date_maturity` | Fecha de vencimiento (o fecha del apunte si no tiene) |
| `days_overdue` | Días vencidos a hoy, nunca negativo |
| `aging_bucket` | Tramo, según la configuración de la compañía |
| `amount_residual` | Saldo pendiente en moneda de la compañía |
| `partner_id`, `commercial_partner_id` | Empresa y empresa matriz |
| `invoice_user_id` | Vendedor, útil para seguimiento de cobros |
| `move_id`, `move_name`, `ref`, `account_id`, `journal_id` | Trazabilidad al asiento |

## Uso

**Contabilidad → Informes → Aged Receivable / Aged Payable.**

Se abre en vista pivote agrupada por tramo. Desde ahí se puede insertar en una
hoja de cálculo o en un tablero con *Insert in Spreadsheet*.

Para usarlo en un tablero propio, cree un pivote sobre `account.aging.analysis`
con `aging_bucket` en filas y `amount_residual` como medida:

```
=PIVOT.VALUE(1,"amount_residual","aging_bucket","bucket_1")
=PIVOT.HEADER(1,"aging_bucket","bucket_1")
```

Si prefiere el tablero ya armado, instale
[`mba_finance_dashboard`](../mba_finance_dashboard).

## Alcance

Se incluyen los apuntes contabilizados, no conciliados y con saldo pendiente
distinto de cero, de cuentas de tipo *Por cobrar* y *Por pagar*. Funciona igual
si los saldos entraron como facturas o como asientos de diario de apertura, lo
cual lo hace apto para el día uno de una migración.

## Licencia

LGPL-3.
