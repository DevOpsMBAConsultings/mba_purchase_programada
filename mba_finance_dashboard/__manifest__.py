{
    'name': 'Tablero Financiero (MBA Consultings)',
    'version': '18.0.1.10.0',
    'category': 'Accounting/Reporting',
    'summary': 'Tablero financiero e inventario listo para usar: antigüedad, posición, resultado del año e inventario operativo',
    'description': 'Tablero que se instala armado, con antigüedad de cuentas por '
                   'cobrar y por pagar, posición neta, estado de resultados del '
                   'año, inventario operativo, déficit de ventas y compras en tránsito.',
    'author': 'MBA Consultings, Brooks Gonzalez',
    'website': 'https://mbaconsultings.com',
    'depends': [
        'mba_account_aging',
        'mba_reportes_diarios',
        'spreadsheet_dashboard',
        'spreadsheet_account',
        'stock',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/dashboard.xml',
        'data/inventory_dashboard.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
