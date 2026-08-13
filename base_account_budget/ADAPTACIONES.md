# Adaptaciones de MBA Consultings

## Origen

Este módulo es una copia de `base_account_budget`, cuyo código fuente original
pertenece a **Cybrosys Techno Solutions** y se publica en
[CybroOdoo/CybroAddons](https://github.com/CybroOdoo/CybroAddons) bajo licencia
**LGPL-3**.

Se conserva la licencia original LGPL-3.

| | |
|---|---|
| Versión base de Cybrosys | `18.0.1.0.0` |
| Estado respecto al upstream | **Sin cambios** |

## Cambios

**Ninguno.** Verificado con `diff -r` contra la rama `18.0` de CybroAddons: el
módulo es byte por byte idéntico al upstream, sin archivos añadidos, modificados
ni eliminados.

## Por qué está en el paquete del cliente

Es dependencia obligatoria de la cadena:

```
dynamic_accounts_report → base_accounting_kit → base_account_budget → account
```

`base_accounting_kit` lo declara en sus `depends`, y sin él no instala
`dynamic_accounts_report`, que es el módulo con las adaptaciones reales.

Se versiona junto al resto para que el despliegue del paquete del cliente sea un
único `git pull`, y para congelar la versión exacta con la que se probó en
producción.

## Mantenimiento

Al no tener divergencias, este módulo puede actualizarse directamente desde el
upstream sin resolver conflictos. Si en algún momento se le añaden cambios
propios, documentarlos aquí.
