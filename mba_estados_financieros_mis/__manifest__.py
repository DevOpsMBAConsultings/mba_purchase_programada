{
    'name': 'Estados Financieros MIS (MBA Consultings)',
    'version': '18.0.1.0.3',
    'category': 'Accounting/Reporting',
    'summary': 'Balance General, Estado de Resultados, Estado de Resultados '
               'de Ventas y Estado de Cambios en el Patrimonio sobre MIS '
               'Builder, agnóstico de plan de cuentas',
    'description': """
Estados Financieros MIS (agnóstico de plan de cuentas)
========================================================

Módulo reutilizable entre clientes de MBA Consultings. No hay ningún
código de cuenta escrito en el módulo: todo se calcula a partir de
``account_type`` (campo obligatorio en cualquier cuenta, de cualquier plan
de cuentas) y, para lo que no tiene un account_type propio, de etiquetas
de cuenta (``account.account.tag``) que cada cliente asigna una sola vez
desde el Plan de Cuentas.

Se apoya en MIS Builder (OCA/mis-builder) y en las plantillas de Balance
General / Estado de Resultados de OCA/account-financial-reporting
(mis_template_financial_report), que ya calculan por account_type.

Reportes que agrega:

1. Balance General y Estado de Resultados (reetiquetados al español, sin
   tocar la lógica de mis_template_financial_report).
2. Estado de Resultados de Ventas: Ventas Netas (account_type='income'),
   Costo de Venta (account_type='expense_direct_cost'), Utilidad Bruta,
   % de Margen, Otros Ingresos (account_type='income_other'). Comisiones
   sobre Venta e ITBMS/IVA cobrado son informativos y dependen de que el
   cliente haya etiquetado la cuenta correspondiente.
3. Estado de Cambios en el Patrimonio: capital (account_type='equity') y
   resultados acumulados (account_type='equity_unaffected') con saldo
   inicial, movimiento del período y saldo final, más una fila de
   verificación contra el saldo real del mayor.

Configuración por cliente (una sola vez, sin código):
Contabilidad > Configuración > Plan de Cuentas > abrir la cuenta > campo
"Etiquetas" > asignar "Comisiones de Venta (MIS)" y/o "Impuesto sobre
Ventas (MIS)" a la(s) cuenta(s) que correspondan en ESE maestro de
cuentas.
""",
    'author': 'MBA Consultings, Brooks Gonzalez',
    'website': 'https://mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': [
        'mis_builder',
        'mis_template_financial_report',
    ],
    'data': [
        'data/account_account_tag.xml',
        'data/mis_report_style.xml',
        'data/mis_report_pl_bs_es.xml',
        'data/mis_report_ventas.xml',
        'data/mis_report_patrimonio.xml',
        'data/mis_report_instance_pl_bs.xml',
        'data/mis_report_instance_ventas.xml',
        'data/mis_report_instance_patrimonio.xml',
        'data/ir_actions_server.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'post_init_hook': 'post_init_hook',
}
