# Estados Financieros MIS (MBA Consultings)

Módulo de solo datos, **agnóstico de plan de cuentas**, que arma 4 reportes
sobre MIS Builder para cualquier cliente de MBA Consultings, tenga o no un
maestro de cuentas propio:

1. **Balance General** y **Estado de Resultados** — reetiquetados al
   español a partir de `mis_template_financial_report` (OCA), sin tocar su
   lógica (agrupa por `account_type`, válido para cualquier plan de
   cuentas).
2. **Estado de Resultados de Ventas** — Ventas Netas
   (`account_type = income`), Costo de Venta
   (`account_type = expense_direct_cost`), Utilidad Bruta, % de Margen,
   Otros Ingresos (`account_type = income_other`). Comisiones sobre Venta
   e ITBMS/IVA Cobrado son informativos y dependen de una etiqueta de
   cuenta (ver abajo).
3. **Estado de Cambios en el Patrimonio** — capital (`account_type =
   equity`) y resultados acumulados (`account_type = equity_unaffected`),
   con saldo inicial, movimiento del período, saldo final y una fila de
   verificación contra el saldo real del mayor. El resultado del período
   se trae por subreporte desde el Estado de Resultados, para que ambos
   estados siempre cuadren entre sí.

## Por qué es agnóstico

Ningún código de cuenta está escrito en este módulo. Todo se calcula a
partir de `account_type`, un campo obligatorio en cualquier cuenta de
cualquier plan de cuentas de Odoo (custom o estándar). Se instala y
funciona en cero configuración sobre cualquier cliente.

Las dos filas que Odoo no clasifica por `account_type` (Comisiones sobre
Venta, ITBMS/IVA) se resuelven con `account.account.tag`. El módulo
instala las etiquetas vacías; cada cliente asigna la etiqueta a SU cuenta
una sola vez desde `Contabilidad > Configuración > Plan de Cuentas >
(abrir la cuenta) > campo "Etiquetas"`. Si no se asigna, esas dos filas
salen en cero — el resto del reporte no se afecta.

## Dependencias

- `mis_builder` (OCA/mis-builder, rama 18.0)
- `mis_template_financial_report` (OCA/account-financial-reporting, rama 18.0)

## Integración a un proyecto de cliente (git subtree)

Este repo vive independiente y se trae a cada proyecto de cliente con
`git subtree`, igual que `mba_purchase_order_format` o
`sale_line_pricelist`. La rama de trabajo es **18.0**:

```bash
git remote add mba_estados_financieros_mis https://github.com/DevOpsMBAConsultings/mba_estados_financieros_mis.git
git subtree add --prefix=mba_estados_financieros_mis mba_estados_financieros_mis 18.0 --squash
```

Para traer actualizaciones futuras del módulo:

```bash
git subtree pull --prefix=mba_estados_financieros_mis mba_estados_financieros_mis 18.0 --squash
```

## Dónde encontrar los reportes

`Contabilidad > Reportes > MIS Reporting > MIS Reports`.

## Checklist de validación antes de usar en producción

- [ ] Correr el Estado de Resultados de Ventas sobre un mes ya cerrado y
      cuadrar "Ventas Netas" contra las facturas de venta de ese mes.
- [ ] Si se quiere ver Comisiones sobre Venta o ITBMS/IVA Cobrado,
      etiquetar la(s) cuenta(s) correspondiente(s) en el Plan de Cuentas
      de ese cliente.
- [ ] En el Estado de Cambios en el Patrimonio: si "Verificación" no
      coincide con el saldo final calculado, puede ser porque el cliente
      aún no corrió el cierre de año fiscal (Odoo calcula el resultado
      del ejercicio al vuelo y solo lo postea a `equity_unaffected` al
      cerrar), o porque hay asientos manuales en esas cuentas que el
      modelo no está capturando.
- [ ] El ITBMS/IVA cobrado depende de que el cliente separe, en su plan
      de cuentas, el impuesto de ventas del de compras (o al menos
      etiquete la porción de ventas). Si todo el IVA/ITBMS vive en una
      sola cuenta neta, esta fila mostrará el movimiento neto del
      período, no el impuesto bruto cobrado.

## Diseño de las expresiones (para quien mantenga esto después)

Las cuentas de tipo `income`, `income_other` y `equity` son de saldo
acreedor: la convención cruda de MIS Builder (`balp`/`bali`/`bale`) las
muestra en negativo, por eso llevan `-` de forma **uniforme**, sin
excepción por cuenta específica. Esto es lo que permite que devoluciones,
descuentos, aportes o retiros -sin importar contra qué cuenta se
contabilicen, siempre que sean del mismo `account_type`- se sumen
correctamente sin casos especiales.

Las cuentas de costo (`expense_direct_cost`) son de saldo deudor: van sin
invertir signo.
