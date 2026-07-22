# -*- coding: utf-8 -*-
{
    'name': 'Redes Sociales en Contactos (Panamá)',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Agrega enlaces de Facebook, Instagram y LinkedIn a los contactos.',
    'description': """
Módulo para agregar campos de redes sociales a los contactos en Odoo 18 y 19.
Ideal para empresas en Panamá que desean tener un acceso rápido a las redes sociales de sus clientes.
    """,
    'author': 'Brooks González / Antigravity',
    'depends': ['base', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
