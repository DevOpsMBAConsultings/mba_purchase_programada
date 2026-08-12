# Panamá - Plan de Cuentas Simplifica T (`l10n_pa_simplificat`)

Plantilla de plan de cuentas contable para Panamá, hecha a medida para el cliente Simplifica T. Se instala como localización fiscal de la compañía en Odoo 18.

## Qué hace

- Registra un juego de cuentas nuevo (plan de cuentas, impuestos por defecto, cuentas de la compañía) bajo el país Panamá.
- Define las cuentas por defecto que Odoo necesita para operar: por cobrar, por pagar, ingresos, gastos, banco, caja, transferencias entre cuentas, diferencia de cambio, descuentos por pronto pago y diferencias de caja.

## Cómo funciona

Usa el decorador `@template('pa_simplificat')`, la forma nativa de Odoo 17+ para declarar plantillas de plan de cuentas (reemplaza al viejo mecanismo de archivos XML de `l10n_xx`). Al crear una compañía y elegir esta plantilla en la configuración fiscal, Odoo:

1. Crea automáticamente todas las cuentas contables definidas en `_get_pa_simplificat_account_account`.
2. Vincula esas cuentas a los campos contables de la compañía (`property_account_receivable_id`, `bank_account_code_prefix`, etc.) definidos en `_get_pa_simplificat_res_company`.

No hay wizards ni vistas — es un módulo de datos que se ejecuta una sola vez, al configurar la compañía.

## Dependencias

- `account`

## Licencia

LGPL-3.
