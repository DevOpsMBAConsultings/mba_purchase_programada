# Estados Financieros MIS (MBA Consultings)

**v18.0.1.0.2**

Módulo de solo datos, **agnóstico de plan de cuentas**, que arma 4 reportes
sobre MIS Builder para cualquier cliente de MBA Consultings, tenga o no un
maestro de cuentas propio.

## Qué reportes trae y qué muestra cada uno

### 1. Balance General

Fotografía de la situación financiera de la empresa **a una fecha
determinada**: qué tiene (activos), qué debe (pasivos) y cuánto es
patrimonio de los socios (activos menos pasivos). Es el reporte que
responde "¿cómo está la empresa hoy?".

- **Plantilla:** `mis_template_financial_report` (OCA), sin modificar su
  lógica — solo se reetiquetó al español.
- **Columnas de la instancia "Balance General - Mensual":** Cierre Mes
  Anterior, A la Fecha, Cierre Año Anterior. Al ser un balance (foto a un
  momento), cada columna representa el saldo acumulado hasta esa fecha,
  no el movimiento de un período.
- **Filas:** Activos (con detalle por cuenta), Pasivos, Patrimonio, y una
  fila de verificación que compara el resultado del Estado de Resultados
  contra lo que hay contabilizado en patrimonio.

### 2. Estado de Resultados

También llamado Estado de Pérdidas y Ganancias. Muestra, **para un
período** (un mes, un año), cuánto entró por ingresos, cuánto salió en
costos y gastos, y si el resultado fue utilidad o pérdida. Es el reporte
que responde "¿ganamos o perdimos, y cuánto?".

- **Plantilla:** `mis_template_financial_report` (OCA), reetiquetada.
- **Columnas de la instancia "Estado de Resultados - Mensual":** Mes
  Anterior, Mes Actual, Acumulado del Año.
- **Filas:** Ingresos (todo lo que es tipo `income`/`income_other`, con
  detalle por cuenta), Costos y Gastos (todo lo que es tipo `expense*`,
  con detalle por cuenta), y la Utilidad o Pérdida del Período como
  resultado final.
- Es el estado general de la empresa. El siguiente reporte es un
  **acercamiento** solo a la parte de ventas.

### 3. Estado de Resultados de Ventas

Un desglose más detallado, enfocado solo en la operación de ventas, útil
para el equipo comercial o para revisar el margen del negocio sin tener
que leer todo el Estado de Resultados general.

- **Plantilla propia** (`report_ventas`), construida sobre este módulo.
- **Columnas de la instancia "Estado de Resultados de Ventas - Mensual":**
  Mes Anterior, Mes Actual, Acumulado del Año.
- **Filas:**
  - **Ventas Netas** — todo lo contabilizado en cuentas de ingreso
    (`account_type = income`), ya neto de devoluciones y descuentos
    (sin importar si se registran contra la misma cuenta de venta o
    contra una cuenta contraria, todo suma con su signo real). Se puede
    expandir para ver el detalle por cuenta de ingreso.
  - **Costo de Venta** — todo lo contabilizado en cuentas de costo
    directo (`account_type = expense_direct_cost`), típicamente el costo
    de la mercancía vendida. También expandible por cuenta.
  - **Utilidad Bruta** — Ventas Netas menos Costo de Venta.
  - **% Margen Bruto sobre Ventas Netas** — Utilidad Bruta ÷ Ventas
    Netas, en porcentaje.
  - **Otros Ingresos No Operacionales** (informativo) — ingresos que no
    son de la operación normal de ventas (intereses ganados, ganancia en
    venta de activos, etc.), separados para no inflar el margen de
    ventas.
  - **Comisiones sobre Venta** (informativo) — solo aparece si se
    etiquetó la cuenta de comisiones (ver sección de configuración).
  - **ITBMS/IVA Cobrado** (informativo) — solo aparece si se etiquetó la
    cuenta correspondiente; ver advertencia sobre neto vs. bruto más
    abajo.

### 4. Estado de Cambios en el Patrimonio

Explica **por qué** cambió el patrimonio de la empresa de un punto a otro
en el tiempo: cuánto había al principio, cuánto se ganó o perdió en el
período, cuánto metieron o sacaron los socios, y cuánto queda al final.
Es el reporte que conecta el Estado de Resultados con el Balance General.

- **Plantilla propia** (`report_patrimonio`), construida sobre este
  módulo. El resultado del período no se recalcula aparte: se trae
  directamente del Estado de Resultados (vía subreporte MIS), así los dos
  estados siempre cuadran entre sí.
- **Columnas de la instancia "Estado de Cambios en el Patrimonio":** Año
  Anterior (Cerrado), Año Actual (Acumulado).
- **Filas:**
  - **Capital - Saldo Inicial / Movimiento / Saldo Final** — aportes,
    retiros y reclasificaciones de capital (`account_type = equity`,
    sin contar el resultado del ejercicio).
  - **Resultados Acumulados - Saldo Inicial** — utilidades de ejercicios
    anteriores que no se han repartido (`account_type =
    equity_unaffected`).
  - **Resultado del Período** — la utilidad o pérdida del período actual,
    tomada del Estado de Resultados.
  - **Resultados Acumulados - Saldo Final** — saldo inicial más el
    resultado del período.
  - **Patrimonio Total - Saldo Final** — Capital final + Resultados
    Acumulados final. Debe coincidir con la fila "Patrimonio" del Balance
    General.
  - **Verificación** (informativo) — el saldo real de las cuentas de
    patrimonio en el mayor, a la fecha de cierre de la columna. Sirve
    para confirmar que el cálculo por movimientos coincide con lo que
    realmente está contabilizado; ver advertencia sobre el cierre de año
    fiscal más abajo.

## Por qué es agnóstico de plan de cuentas

Ningún código de cuenta está escrito en este módulo. Todo se calcula a
partir de `account_type`, un campo obligatorio en cualquier cuenta de
cualquier plan de cuentas de Odoo (custom o estándar). Se instala y
funciona en cero configuración sobre cualquier cliente.

Las dos filas que Odoo no clasifica por `account_type` (Comisiones sobre
Venta, ITBMS/IVA) se resuelven con `account.account.tag`. El módulo
instala las etiquetas vacías; cada cliente asigna la etiqueta a SU cuenta
una sola vez desde `Contabilidad > Configuración > Plan de Cuentas >
(abrir la cuenta) > campo "Etiquetas"`:

- **Comisiones de Venta (MIS)** → cuenta donde se registra el gasto de
  comisiones de vendedores.
- **Impuesto sobre Ventas (MIS)** → cuenta de impuesto (ITBMS/IVA) por
  pagar.

Si no se asigna la etiqueta, esa fila sale en cero — el resto del reporte
no se afecta.

## Tema visual (colores de marca del cliente)

Los 4 reportes comparten una misma jerarquía visual de 3 niveles, definida
en `data/mis_report_style.xml`:

- **Fila de detalle** (cuenta individual): sin color, texto normal.
- **Subtotal** (`style_subtotal` / `style_subtotal_indent`): fondo azul
  claro `#D9DEEB`, negrita.
- **Total** (`style_total`): fondo azul marino `#012177` (color principal
  de la marca), texto blanco, negrita.

Estos dos tonos de azul son los mismos que ya están configurados en
`Ajustes > Ajustes Generales > Diseño del Documento` (la plantilla de
cotizaciones/facturas de Simplifica T), para que el reporte financiero se
vea consistente con el resto de la papelería de la empresa. El rojo de esa
misma plantilla (`#AE1E16`) se dejó fuera a propósito: en un estado
financiero el rojo se asocia a pérdida o saldo negativo, así que usarlo
como color decorativo de fila generaría confusión.

Balance General y Estado de Resultados (que reutilizan la plantilla de
`mis_template_financial_report` de OCA) traían sus propios estilos, solo
negrita sin color. Se les apuntó el `style_id` a nuestros propios estilos
(ver `data/mis_report_pl_bs_es.xml`) para que los 4 reportes luzcan con el
mismo tema. Esto se hace actualizando un campo de un registro existente
desde nuestro módulo -no se toca ningún archivo de OCA-, así que sobrevive
actualizaciones del módulo OCA sin conflicto.

Si el cliente cambia su paleta de marca más adelante, solo hay que
actualizar los 2 colores en `style_subtotal` / `style_subtotal_indent` /
`style_total` en `data/mis_report_style.xml` y subir la versión; se
propaga automáticamente a los 4 reportes.

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

**Corchetes anidados:** el parser de expresiones de MIS Builder usa una
expresión regular NO-GREEDY para extraer el dominio entre corchetes
(`balp[...]`), así que se detiene en el PRIMER `]` que encuentra. No se
pueden anidar listas dentro del dominio — por ejemplo `('tag_ids', 'in',
[x])` rompe el parseo porque el `]` de la lista interna cierra el match
antes de tiempo. Por eso:
- El filtro por etiqueta usa `'tag_ids', '='` con un solo id, no `'in'`
  con una lista (para campos many2many, `'='` con un id equivale a
  "contiene ese id").
- La fila de verificación de patrimonio usa `'like', 'equity%'` en vez de
  `'in', ['equity', 'equity_unaffected']`, aprovechando que ambos
  `account_type` comparten el prefijo `equity`.

## Historial de cambios

- **18.0.1.0.2** — Alinea el tema visual de los 4 reportes a los colores
  de marca del cliente (azul marino `#012177`, tomado de la plantilla de
  cotizaciones/facturas). Balance General y Estado de Resultados ahora
  usan los mismos estilos `style_subtotal` / `style_total` que Ventas y
  Patrimonio, en vez de los estilos por defecto (sin color) de
  `mis_template_financial_report`. Ver sección "Tema visual" arriba.
- **18.0.1.0.1** — Corrige dos bugs de instalación: el campo `divider` de
  `mis.report.style` no acepta `'total'` como valor (es un factor de
  escala numérico, no un tipo de línea); y dos expresiones usaban listas
  anidadas dentro de corchetes, que el parser de MIS Builder no soporta.
- **18.0.1.0.0** — Versión inicial.
