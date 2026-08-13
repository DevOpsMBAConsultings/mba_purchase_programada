# MBA - Importador de Cotizaciones PDF (`mba_importador_cotizaciones_pdf`)

Importa cotizaciones y comprobantes electrónicos (CAFE DGI/HKA) directamente desde un archivo PDF, sin depender de APIs de pago ni de servicios de IA.

## Qué hace

- Extracción de datos **100% local y offline**: no envía el PDF a ningún servicio externo.
- Soporta importación individual o por lotes (varios PDF a la vez).
- **Homologación de clientes**: si el cliente que aparece en el PDF no existe en la base de datos, la cotización se asigna automáticamente al partner "Consumidor Final", pero conserva el nombre original del PDF para auditoría — no se pierde el dato, solo se homologa.
- **Productos no encontrados**: si una línea del PDF no coincide con ningún producto del catálogo, se importa igual sin producto vinculado, manteniendo descripción, cantidad, precio e impuesto, para que el vendedor la revise y complete manualmente.
- Adjunta el PDF original al chatter (historial de mensajes) del pedido en estado borrador.
- Muestra una alerta visual en la cabecera de la cotización cuando la importación generó advertencias.

## Cómo funciona

El parser (`wizard/pdf_parser.py`) usa la librería **PyMuPDF** (`fitz`) para leer el texto y los bloques de un PDF localmente. Primero detecta el tipo de documento buscando marcadores de texto característicos (por ejemplo "Comprobante Auxiliar", "DGI", "FE01"/"FE04" en el nombre del archivo, o "Protocolo de autorización"):

- Si es un **comprobante electrónico DGI/HKA (CAFE)**, aplica un parser específico para ese formato, extrayendo nombre/RUC/DV del cliente con expresiones regulares sobre los bloques de texto.
- Si no, lo trata como una **cotización genérica** y usa un parser distinto.

En ambos casos extrae cabecera (cliente, fecha, vendedor, número, términos de pago), líneas de detalle (cantidad, código, descripción, impuesto, precio, subtotal) y totales, y con eso arma un `sale.order` en Odoo.

## Dependencias

- `sale_management`, `mail`

## Licencia

LGPL-3.
