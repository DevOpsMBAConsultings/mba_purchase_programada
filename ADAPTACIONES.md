# Adaptaciones de MBA Consultings

## Origen

Este módulo es una adaptación de `dynamic_accounts_report`, cuyo código fuente
original pertenece a **Cybrosys Techno Solutions** y se publica en
[CybroOdoo/CybroAddons](https://github.com/CybroOdoo/CybroAddons) bajo licencia
**LGPL-3**.

MBA Consultings lo modificó para adaptarlo a las necesidades de sus clientes.
Se conserva la licencia original LGPL-3.

| | |
|---|---|
| Versión base de Cybrosys | `18.0.1.3.4` (commit `a7e2384`) |
| Alcance de las adaptaciones | 21 archivos, ~926 líneas añadidas / 738 eliminadas |

> **Nota de mantenimiento.** El upstream ya publicó `18.0.1.3.5`, que toca
> `models/account_trial_balance.py`, `models/dynamic_balance_sheet_report.py`,
> `models/tax_report.py`, `doc/RELEASE_NOTES.md`, `__manifest__.py` y
> `static/description/index.html`. Los tres primeros archivos tienen también
> cambios nuestros, así que el merge de esa versión requiere revisión manual.
> `tax_report.py` no tiene cambios nuestros y puede tomarse tal cual del upstream.

---

## 1. Rendimiento: eliminación de consultas N+1

El patrón original recorría las cuentas (o los partners) y, **dentro del bucle**,
ejecutaba un `search` o un `filtered` seguido de un `read` por cada registro. Con
un plan de cuentas mediano eso significa cientos de consultas por cada apertura
de reporte.

Se sustituyó por agregación previa fuera del bucle.

### `models/account_trial_balance.py`

Dos `search` de `account.move.line` por cada cuenta pasaron a dos `read_group`
agregados, más un diccionario indexado por cuenta:

```python
init_groups = self.env['account.move.line'].read_group(
    [('date', '<', month_start), ('parent_state', '=', 'posted'),
     ('account_id', 'in', account_ids.ids)],
    ['account_id', 'debit:sum', 'credit:sum'], ['account_id'], lazy=False)
init_by_acc = {x['account_id'][0]: (round(x['debit'], 2), round(x['credit'], 2))
               for x in init_groups if x.get('account_id')}
```

También se sacó del bucle el `search_read` de `account.journal`, que se repetía
por cada cuenta.

### `models/account_general_ledger.py`, `bank_book_report.py`, `cash_book_report.py`

Mismo criterio con un `read()` masivo único y agrupación en Python vía
`collections.defaultdict`, en lugar de `filtered()` por cuenta:

```python
all_lines_data = move_line_ids.read([...])
lines_by_acc = defaultdict(list)
for line_data in all_lines_data:
    if line_data.get('account_id'):
        lines_by_acc[line_data['account_id'][0]].append(line_data)
```

### `models/aged_payable_report.py`, `aged_receivable_report.py`

Igual: un `read()` masivo, cálculo de los tramos de antigüedad en una sola
pasada, y agrupación por partner con `defaultdict`.

---

## 2. Carga diferida en el Libro Mayor de Terceros

`models/account_partner_ledger.py` — el cambio de mayor alcance.

El original devolvía **todos** los apuntes de **todos** los partners en la
llamada inicial. Con varios cientos de terceros y miles de apuntes, la pantalla
tardaba en abrir aunque el usuario solo fuera a mirar uno.

La versión adaptada devuelve únicamente los totales agregados y deja las líneas
vacías:

```python
partner_dict[p_name] = []  # Empty list for lazy loading
```

Los apuntes se piden bajo demanda mediante un método nuevo, **`get_partner_lines()`**,
que no existe en el upstream. El frontend se adaptó en consecuencia:
`static/src/js/partner_ledger.js` lo invoca al expandir un tercero.

Los totales y el saldo inicial se calculan con `read_group` sobre dos dominios
(global y anterior al inicio del ejercicio).

---

## 3. Presentación de importes

Criterio contable aplicado de forma transversal en las plantillas:

- **Alineación a la derecha** de todas las columnas numéricas (el original las
  centraba). La primera columna se mantiene a la izquierda.
- **Símbolo de moneda** en cada celda de importe. Los modelos añaden
  `currency_symbol` al diccionario de datos.
- **Formato con separador de miles y dos decimales fijos**, vía
  `toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})`
  en las plantillas OWL.

Archivos afectados: `static/src/xml/trial_balance_view.xml`,
`balance_sheet_template.xml`, `partner_ledger_view.xml`,
`profit_and_loss_templates.xml`, `tax_report_views.xml`,
`aged_payable_report_views.xml`, `general_ledger_view.xml`,
`bank_flow_templates.xml`, `cash_flow_templates.xml`, y
`static/src/css/accounts_report.css`.

### Formateo movido del modelo a la vista

En `models/dynamic_balance_sheet_report.py` se eliminaron los
`"{:,.2f}".format(...)` del lado Python; el modelo ahora devuelve números crudos
y el formateo ocurre en la plantilla. Esto evita el doble formateo y permite
reutilizar los valores en cálculos.

En `aged_receivable_report.py` se conservan **ambas** versiones: los campos
`raw_*` con el valor numérico y los formateados para presentación, porque la
exportación a XLSX necesita el número.

---

## 4. Corrección de errores

### `date_maturity` vacío rompía los reportes de antigüedad

En `aged_payable_report.py` y `aged_receivable_report.py`, el upstream calcula:

```python
diffrence = (today - val['date_maturity']).days
```

sin verificar que `date_maturity` tenga valor. Un apunte sin fecha de
vencimiento provoca `TypeError`. La versión adaptada inicializa la diferencia en
cero y solo la calcula si el campo existe:

```python
diffrence = 0
if val['date_maturity']:
    diffrence = (today - val['date_maturity']).days
```

---

## 5. Cambio de semántica en el Balance de Comprobación

**Importante para quien compare contra el reporte original.**

El upstream construía la lista de cuentas a partir de los apuntes existentes:

```python
account_ids = self.env['account.move.line'].search([]).mapped('account_id')
```

La versión adaptada parte del plan de cuentas completo y descarta después las
que quedan en cero:

```python
account_ids = self.env['account.account'].search([])
...
if initial_total_debit == 0.0 and initial_total_credit == 0.0 \
        and total_debit == 0.0 and total_credit == 0.0:
    continue
```

El resultado visible es equivalente en la mayoría de los casos, pero el punto de
partida es distinto. Además, `account_general_ledger.py` añade una columna de
**saldo** (`balance` y `balance_display`) que el original no calculaba, y agrupa
los apuntes por asiento (`move_id`) en lugar de listarlos planos.

---

## 6. Traducción al español de Panamá

Se añadió `i18n/es_PA.po` (2.409 líneas), inexistente en el upstream.

---

## 7. Limpieza posterior a la puesta en Git

Corregido en `18.0.1.3.4.1`, después del snapshot de producción:

- **Código de depuración eliminado.** `models/account_partner_ledger.py` tenía
  dos bloques con `import logging` dentro del método y un
  `_logger.info("VIEW_REPORT RETURNING: ...")` que escribía en el log de
  producción cada vez que se abría el reporte. El logger pasó a nivel de módulo
  y el mensaje se eliminó.
- **Docstrings repuestos** en `view_report`, `get_filter_values` y
  `get_partner_lines`. Este último es método propio de MBA y no tenía ninguno.
- **32 líneas con espacios en blanco al final** limpiadas.
- **CSS consolidado**: tres bloques de reglas duplicados para
  `.table_main_view table th, td` reducidos a uno. El segundo anulaba el
  `padding` del primero, que quedaba muerto.

---

## Versionado

**La versión del manifest se congela en la de Cybrosys** (`18.0.1.3.4`). Los
cambios de MBA se registran en este archivo y en el historial de git, no en el
número de versión.

Es una excepción deliberada a la regla de subir el patch en cada cambio, y
tiene dos motivos:

1. **Odoo 18 no admite un segmento adicional.** `odoo/modules/module.py`,
   función `adapt_version`, valida con
   `^[0-9]+\.[0-9]+(?:\.[0-9]+)?$` sobre la versión sin el prefijo de serie.
   Un `18.0.1.3.4.1` deja `1.3.4.1`, cuatro segmentos, y el módulo se descarta
   con `ValueError: invalid manifest` — no aparece siquiera en la lista de
   aplicaciones.
2. **Cualquier incremento colisiona con el upstream.** Cybrosys ya publicó su
   propio `18.0.1.3.5`; si MBA subiera el patch, dos releases distintos
   compartirían número.

Como el despliegue se hace siempre con `-u <módulo>` explícito, congelar la
versión no impide actualizar.

---

## Deuda pendiente

Elementos identificados durante la revisión, aún sin corregir:

| | Archivo | Detalle |
|---|---|---|
| 1 | `models/*.py` | Siete usos de `read_group`. Vigente en Odoo 18 — el propio módulo `account` lo sobrescribe en `account_bank_statement_line.py` — pero Odoo migra hacia `_read_group`. Verificar antes del port a Odoo 19. |
| 2 | `models/account_partner_ledger.py` | `partner_dict` se indexa por **nombre** de partner; dos terceros homónimos se pisan. Defecto heredado del upstream, no introducido aquí, pero el bloque ya fue reescrito y el cambio a `id` sería barato. |
| 3 | `static/src/js/trial_balance.js` | `console.log("amrutha test")` en la línea 183. **Heredado del upstream de Cybrosys**, no introducido por MBA. |
| 4 | `models/account_partner_ledger.py` | Avisos de estilo preexistentes: líneas de más de 120 caracteres (E501), sentencias `if x: y` en una sola línea (E701) y comentarios inline sin doble espacio (E261). Cosmético; se dejó tal cual para no ensuciar el diff contra el upstream. |
