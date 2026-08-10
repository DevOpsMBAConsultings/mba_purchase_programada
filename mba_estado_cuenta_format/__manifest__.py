{
    'name': 'Formato de Estado de Cuenta (MBA Consultings)',
    'version': '18.0.1.0.1',
    'category': 'Accounting/Reporting',
    'summary': 'Formato de Estado de Cuenta personalizado (Azul/Rojo), '
               'homogéneo con Cotización y Orden de Compra',
    'description': """
Formato de Estado de Cuenta (MBA Consultings)
================================================

Reemplaza el layout de los DOS reportes de estado de cuenta del módulo
OCA ``partner_statement`` -que son plantillas distintas, cada una con su
propio encabezado-:

- ``partner_statement.outstanding_statement`` ("Estado de los
  pendientes de la cuenta del cliente", solo saldos pendientes).
- ``partner_statement.activity_statement`` ("Estado de la cuenta del
  cliente", historial completo de movimientos).

por el mismo patrón visual ya usado en ``formato_cotizacion_simplificat``
y ``mba_purchase_order_format``: logo y datos de encabezado corporativo
(azul ``#04167e`` / rojo ``#cb1a1c``), en vez del layout genérico de
Odoo (Light/Boxed/Bold/etc.).

Por qué existe
--------------
El reporte de Estado de Cuenta usaba ``web.external_layout``, el
despachador genérico de Odoo que elige entre 7 layouts posibles según el
Diseño de Documentos configurado en la empresa. Ese despachador delega el
encabezado (logo + datos de empresa) a un contenedor flexbox
(``.row``/``.col-*`` o ``.d-flex`` de Bootstrap 5) que wkhtmltopdf no
pinta de forma confiable en PDF (ver ``mba_pdf_header_logo_fix`` para el
diagnóstico completo de esa causa raíz). En vez de perseguir los 7
layouts uno por uno, este módulo saca a este reporte específico de ese
despachador -igual que ya se hizo con Cotización y Orden de Compra- y le
da su propio encabezado, fijo y probado.

Qué cambia
----------
- Cambia ``t-call="web.external_layout"`` por ``t-call="web.basic_layout"``
  (sin mecanismo de header repetido de wkhtmltopdf).
- Reemplaza el bloque "Statement of Account" + fila de información por un
  encabezado de dos columnas: logo + datos del cliente (izquierda),
  "Estado de Cuenta" + fecha/código de cliente/RUC (derecha).
- Restylea las tablas de saldo pendiente y antigüedad de saldos
  (``table-statement``, de ``partner_statement.outstanding_balance`` /
  ``partner_statement.aging_buckets``) con los mismos colores de marca,
  vía CSS con alcance al reporte -no se toca ningún archivo de OCA.
- No cambia ningún dato ni cálculo: mismas filas, mismos totales, mismo
  ``d``/``o`` que ya calculaba el módulo OCA.

Dependencias
------------
Requiere el módulo OCA ``partner_statement``
(OCA/account-financial-reporting, rama 18.0), ya instalado en este
cliente.

Alcance
-------
Módulo específico de Simplifica T (colores de marca fijos, igual que
``formato_cotizacion_simplificat`` y ``mba_purchase_order_format``): no
vive en un repo reutilizable aparte. Si otro cliente de MBA Consultings
necesita el mismo tratamiento, se copia este módulo y se ajustan los
colores/campos, siguiendo el mismo patrón que los otros dos formatos.
""",
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': [
        'partner_statement',
    ],
    'data': [
        'views/report_outstanding_statement.xml',
        'views/report_activity_statement.xml',
    ],
    'installable': True,
    'application': False,
}
