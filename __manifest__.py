# -*- coding: utf-8 -*-
{
    'name': 'MBA - Importador de Cotizaciones PDF (MBA Consultings)',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Importación automática y agnóstica de cotizaciones en PDF con homologación y alertas de auditoría',
    'description': """
MBA - Importador de Cotizaciones PDF
=====================================
Módulo agnóstico de importación de cotizaciones en formato PDF para Odoo 18.0 CE.

Características principales:
---------------------------
* Extracción local 100% offline (sin dependencias de API de pago ni consumo de tokens de IA).
* Soporte para importación de cotizaciones individuales o por lotes masivos.
* Homologación inteligente de clientes: si no se encuentra al cliente original del PDF en la base de datos, se asigna automáticamente al partner "Consumidor Final" preservando el nombre original en auditoría.
* Manejo de productos no encontrados (Opción 1): importación de líneas sin producto vinculado, manteniendo la descripción, cantidad, precio e impuesto para verificación del vendedor.
* Alerta visual nativa en la cabecera de la cotización cuando existen advertencias de importación.
* Adjunto automático de cada documento PDF original en el Chatter (mail.message) del pedido en estado borrador.
    """,
    'author': 'MBA Consultings, Brooks Gonzalez',
    'website': 'https://www.mbaconsultings.com',
    'depends': ['sale_management', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/sale_order_import_pdf_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
