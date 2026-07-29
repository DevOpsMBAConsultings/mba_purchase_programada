# Adaptaciones de MBA Consultings

## Origen

Este módulo es una adaptación de `base_accounting_kit`, cuyo código fuente
original pertenece a **Cybrosys Techno Solutions** y se publica en
[CybroOdoo/CybroAddons](https://github.com/CybroOdoo/CybroAddons) bajo licencia
**LGPL-3**.

Se conserva la licencia original LGPL-3.

| | |
|---|---|
| Versión base de Cybrosys | `18.0.5.0.9` |
| Estado respecto al upstream | Idéntico salvo un archivo añadido |

## Cambios

Se añadió **`i18n/es_PA.po`** (4.132 líneas), traducción al español de Panamá
inexistente en el upstream.

**No hay cambios de código.** El resto del módulo es byte por byte idéntico a la
versión `18.0.5.0.9` de Cybrosys, verificado con `diff -r` contra la rama `18.0`
de CybroAddons.

## Por qué está en el paquete del cliente

Además de la traducción, este módulo es una dependencia obligatoria de la cadena:

```
dynamic_accounts_report → base_accounting_kit → base_account_budget → account
```

`dynamic_accounts_report`, que sí tiene adaptaciones sustanciales, no instala sin
él.

## Notas de despliegue

Declara dependencias de Python que deben estar instaladas en el servidor:

```
openpyxl, ofxparse, qifparse
```

Es el único de los tres módulos marcado como `application: True`.
