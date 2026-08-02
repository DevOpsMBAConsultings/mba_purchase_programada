{
    'name': 'Tablero Financiero (MBA Consultings)',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Tablero financiero listo para usar: antigüedad, posición y resultado del año',
    'description': 'Tablero que se instala armado, con antigüedad de cuentas por '
                   'cobrar y por pagar, posición neta, estado de resultados del '
                   'año y top de empresas con saldo vencido.',
    'author': 'MBA Consultings, Brooks Gonzalez',
    'website': 'https://mbaconsultings.com',
    'depends': [
        'mba_account_aging',
        'spreadsheet_dashboard',
        'spreadsheet_account',
    ],
    'data': [
        'data/dashboard.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
