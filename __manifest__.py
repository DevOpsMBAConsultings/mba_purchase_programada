{
    'name': 'Aged Balance Analysis',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Pivotable ageing of receivables and payables by days past due',
    'description': 'Open customer and vendor items classified into configurable '
                   'ageing buckets, computed live in SQL and usable in pivots, '
                   'graphs, spreadsheets and dashboards.',
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
