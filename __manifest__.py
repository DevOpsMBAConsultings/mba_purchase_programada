{
    'name': 'Corrección de Logo en Encabezado PDF (MBA Consultings)',
    'version': '18.0.1.0.2',
    'category': 'Technical',
    'summary': 'Corrige el logo/datos de empresa que no se pintan en el '
               'encabezado de los reportes PDF (Estado de Cuenta y '
               'cualquier reporte que use el layout estándar de Odoo)',
    'description': """
Corrección de Logo en Encabezado PDF
======================================

Problema
--------
En reportes PDF generados con wkhtmltopdf (el motor estándar de Odoo CE),
el logo de la empresa y el bloque de dirección no se pintan en el
encabezado cuando el layout de documentos activo es Light (standard),
Boxed o Bold. La vista previa HTML dentro de Odoo se ve bien; el problema
es exclusivo del PDF.

Causa raíz
----------
El bloque "header" de estos 3 layouts (``web.external_layout_standard``,
``web.external_layout_boxed``, ``web.external_layout_bold``) se extrae y
se pasa a wkhtmltopdf como un archivo HTML aparte (parámetro header-html),
que wkhtmltopdf renderiza en un sub-proceso de WebKit distinto -y más
limitado- al que usa para el cuerpo del documento. Ese sub-proceso tiene
soporte pobre de flexbox/CSS Grid (los 3 layouts usan ``.row``/``.col-*``
o ``.d-flex`` de Bootstrap 5, que son flexbox), y ahí es donde falla: la
imagen queda embebida en el PDF (se puede confirmar inspeccionando el PDF
con Ghostscript) pero wkhtmltopdf no la pinta en el lienzo del header.

No es un problema de:
- Caché del navegador (se confirmó generando el PDF directo en el
  servidor con ``ir.actions.report._render_qweb_pdf``, sin pasar por
  el navegador).
- Configuración de Diseño de Documentos (se probó Standard/Boxed/Bold,
  falla en los 3).

Como referencia de que SÍ funciona fuera del header: un reporte de
cotización custom (Simplifica T) muestra el logo bien en PDF porque
coloca el ``<img>`` fuera del bloque header compartido (con
``web.basic_layout`` en vez de ``web.external_layout``), es decir, como
parte del cuerpo normal del documento, no del header repetido de
wkhtmltopdf. Esa técnica pierde la repetición del logo en cada página,
por lo que no es apta para reportes largos como un Estado de Cuenta.

Solución de este módulo
------------------------
En vez de sacar el logo del header (lo que perdería la repetición del
logo en cada página), este módulo hereda por XPath el bloque del header
de los 3 layouts y reemplaza el contenedor flexbox (``.row``/``.d-flex``)
por una tabla HTML simple (``<table><tr><td>...``), que es el patrón que
los motores WebKit antiguos (como el que usa wkhtmltopdf) sí renderizan
de forma confiable -es la técnica clásica de compatibilidad para motores
de render viejos (el mismo motivo por el que los emails HTML antiguos se
maquetan con tablas). También se agrega un ``max-height`` explícito en
línea al ``<img>`` del logo, para no depender de que el bundle de CSS de
impresión haya cargado bien en el sub-proceso del header.

No se modifica ningún archivo del módulo ``web`` de Odoo ni de OCA: todo
se hace vía ``inherit_id`` + XPath sobre los templates QWeb, así que
sobrevive actualizaciones de Odoo sin conflicto y sin tocar nada a mano
en la base de datos.

Detalle técnico de los XPath
-----------------------------
El div "header" de estos templates usa ``t-attf-class`` (calculado en
runtime), no un ``class=`` literal, así que un XPath ``hasclass('header')``
sobre ese div NO lo detecta (``hasclass()`` opera sobre el arch/XML crudo,
antes de resolver ``t-attf-class``). Por eso cada XPath de este módulo
apunta directo al div interno con clase estática (row/d-flex), combinando
dos clases cuando hace falta para no chocar con los divs placeholder
("bg-light ... d-flex...") de dirección vacía que existen más abajo en el
mismo template. Cada expresión fue verificada contra el código fuente de
Odoo 18 CE para confirmar que matchea exactamente un nodo por template:

- Bold: ``//div[hasclass('row')]``
- Boxed: ``//div[hasclass('row') and hasclass('mb8')]``
- Standard: ``//div[hasclass('d-flex') and hasclass('justify-content-between')]``

Alcance
-------
Cubre los 3 layouts "profesionales" (Light/Standard, Boxed, Bold), que
son los que se probaron y fallan. Los layouts Striped, Bubble, Wave y
Folder no están cubiertos todavía -si algún cliente los usa y presenta el
mismo síntoma, se extiende este mismo módulo con el mismo patrón.

Este módulo es agnóstico de cliente: no depende de nada específico de
ningún cliente de MBA Consultings, por lo que vive en su propio repo
reutilizable (igual que ``mba_estados_financieros_mis``) y se integra a
cada repo de cliente vía ``git subtree``.
""",
    'author': 'MBA Consultings, Brooks Gonzalez',
    'website': 'https://mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],
    'data': [
        'views/report_templates.xml',
    ],
    'installable': True,
    'application': False,
}
