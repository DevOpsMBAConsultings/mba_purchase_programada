{
    'name': 'Finance Overview Dashboard (MBA Consultings)',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Ready-made finance dashboard: ageing, position and year-to-date result',
    'description': 'Pre-built spreadsheet dashboard showing aged receivables and '
                   'payables, net position, year-to-date profit and loss, and top '
                   'overdue partners. Installs ready to use.',
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
