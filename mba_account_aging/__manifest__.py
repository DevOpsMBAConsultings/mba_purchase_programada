{
    'name': 'Antigüedad de Saldos (MBA Consultings)',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Antigüedad de cuentas por cobrar y por pagar, analizable en pivote',
    'description': 'Clasifica los apuntes abiertos de clientes y proveedores en '
                   'tramos de días vencidos configurables, calculados en vivo '
                   'sobre una vista SQL y usables en pivotes, gráficos, hojas '
                   'de cálculo y tableros.',
    'author': 'MBA Consultings, Brooks Gonzalez',
    'website': 'https://mbaconsultings.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/aging_security.xml',
        'views/res_config_settings_views.xml',
        'views/aging_analysis_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
