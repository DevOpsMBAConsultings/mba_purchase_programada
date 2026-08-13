# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Bhagyadev KP (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import io
import json
import logging
from dateutil.relativedelta import relativedelta
import xlsxwriter
from odoo import api, fields, models
from datetime import datetime
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class AccountPartnerLedger(models.TransientModel):
    """For creating Partner Ledger report"""
    _name = 'account.partner.ledger'
    _description = 'Partner Ledger Report'

    @api.model
    def view_report(self, option, tag):
        """
        Devuelve los totales por tercero para el Libro Mayor de Terceros.

        A diferencia de la version original de Cybrosys, no carga los apuntes:
        los importes se agregan con read_group y la lista de lineas de cada
        tercero se deja vacia para carga diferida (ver ``get_partner_lines``).

        :param option: Opcion de filtrado de los datos.
        :type option: str
        :param tag: Etiqueta usada para filtrar.
        :type tag: str
        :return: Diccionario {nombre_tercero: []} mas la clave
            ``partner_totals`` con debe, haber y saldo inicial de cada uno.
        :rtype: dict
        """
        fiscal_year = self.env['res.company'].search([]).mapped('account_opening_date')[0].strftime('%Y-%m-%d')
        fiscal_year_start = datetime.strptime(fiscal_year, '%Y-%m-%d').date()

        partner_dict = {}
        partner_totals = {}

        base_domain = [
            ('account_type', 'in', ['liability_payable', 'asset_receivable']),
            ('parent_state', '=', 'posted')
        ]

        # 1. Get partners and totals grouped
        move_lines_grouped = self.env['account.move.line'].read_group(
            base_domain, ['partner_id', 'debit', 'credit'], ['partner_id']
        )
        totals_map = {r['partner_id'][0]: {'debit': r['debit'], 'credit': r['credit']} for r in move_lines_grouped if r['partner_id']}

        # 2. Get initial balance (invoice_date < fiscal_year_start)
        init_domain = base_domain + [('invoice_date', '<', fiscal_year_start)]
        init_grouped = self.env['account.move.line'].read_group(
            init_domain, ['partner_id', 'debit', 'credit'], ['partner_id']
        )
        init_map = {r['partner_id'][0]: {'debit': r['debit'], 'credit': r['credit']} for r in init_grouped if r['partner_id']}

        partner_ids = list(totals_map.keys())
        if not partner_ids:
            return {}

        currency_id = self.env.company.currency_id.symbol
        partner_recs = self.env['res.partner'].browse(partner_ids)
        partner_names = {p.id: p.name for p in partner_recs}

        for p_id in partner_ids:
            p_name = partner_names.get(p_id, 'Unknown')
            t_debit = totals_map.get(p_id, {}).get('debit', 0.0)
            t_credit = totals_map.get(p_id, {}).get('credit', 0.0)

            init_debit = init_map.get(p_id, {}).get('debit', 0.0)
            init_credit = init_map.get(p_id, {}).get('credit', 0.0)
            init_balance = init_debit - init_credit

            partner_dict[p_name] = [] # Empty list for lazy loading
            partner_totals[p_name] = {
                'total_debit': round(t_debit, 2),
                'total_credit': round(t_credit, 2),
                'currency_id': currency_id,
                'initial_balance': init_balance,
                'partner_id': p_id,
                'move_name': 'Initial Balance',
                'initial_debit': init_debit,
                'initial_credit': init_credit,
            }

        partner_dict['partner_totals'] = partner_totals
        return partner_dict

    @api.model
    def get_filter_values(self, partner_id, data_range, account, options, tag_ids=None, account_ids=None):
        """
        Devuelve los totales por tercero aplicando los filtros de la pantalla.

        Equivalente a ``view_report`` pero acotado por tercero, rango de
        fechas, tipo de cuenta y estado del asiento.

        :param partner_id: Id o ids de los terceros a filtrar.
        :type partner_id: list or int
        :param data_range: Rango de fechas ('month', 'year', 'quarter',
            'last-month', 'last-year', 'last-quarter' o un dict con
            ``start_date`` / ``end_date``).
        :type data_range: str or dict
        :param account: Tipos de cuenta a incluir ('Receivable', 'Payable').
        :type account: list or str
        :param options: Opciones adicionales; si incluye 'draft' se suman los
            asientos en borrador a los asentados.
        :type options: dict
        :param tag_ids: Etiquetas analiticas por las que filtrar.
        :param account_ids: Cuentas concretas por las que filtrar.
        :return: Diccionario con los datos filtrados de los terceros.
        :rtype: dict
        """
        if options == {}: options = None
        if account == {}: account = None
        account_type_domain = []
        if options is None:
            option_domain = ['posted']
        elif 'draft' in options:
            option_domain = ['posted', 'draft']

        if account is None or ('Receivable' in account and 'Payable' in account):
            account_type_domain.extend(['liability_payable', 'asset_receivable'])
        elif 'Receivable' in account:
            account_type_domain.append('asset_receivable')
        elif 'Payable' in account:
            account_type_domain.append('liability_payable')

        partner_dict = {}
        partner_totals = {}
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        previous_quarter_start = quarter_start - relativedelta(months=3)
        previous_quarter_end = quarter_start - relativedelta(days=1)

        # Handle partner tag filter
        if tag_ids:
            partners_with_tags = self.env['res.partner'].search([('category_id', 'in', tag_ids)])
            if partner_id:
                partner_id = list(set(partner_id) & set(partners_with_tags.ids))
            else:
                partner_id = partners_with_tags.ids

        base_domain = [
            ('account_type', 'in', account_type_domain),
            ('parent_state', 'in', option_domain)
        ]
        if account_ids:
            base_domain.append(('account_id', 'in', account_ids))

        if not partner_id:
            # OPTIMIZATION: read_group instead of search().mapped()
            res = self.env['account.move.line'].read_group(base_domain, ['partner_id'], ['partner_id'])
            partner_id = [r['partner_id'][0] for r in res if r['partner_id']]

        if not partner_id:
            return {'partner_totals': {}}

        # Add partner domain
        base_domain.append(('partner_id', 'in', partner_id))

        # Determine period and initial balance date
        domain = list(base_domain)
        balance_domain = list(base_domain)
        date_start = False

        if data_range:
            if data_range == 'month':
                date_start = today.replace(day=1)
                domain.extend([('date', '>=', date_start), ('date', '<=', today)])
                balance_domain.append(('invoice_date', '<', date_start))
            elif data_range == 'year':
                date_start = today.replace(month=1, day=1)
                domain.extend([('date', '>=', date_start), ('date', '<=', today)]) # or whole year
                balance_domain.append(('invoice_date', '<', date_start))
            elif data_range == 'quarter':
                date_start = quarter_start
                domain.extend([('date', '>=', date_start), ('date', '<=', quarter_end)])
                balance_domain.append(('invoice_date', '<', date_start))
            elif data_range == 'last-month':
                date_start = today.replace(day=1) - relativedelta(months=1)
                date_end = today.replace(day=1) - relativedelta(days=1)
                domain.extend([('date', '>=', date_start), ('date', '<=', date_end)])
                balance_domain.append(('invoice_date', '<', date_start))
            elif data_range == 'last-year':
                date_start = today.replace(month=1, day=1) - relativedelta(years=1)
                date_end = today.replace(month=1, day=1) - relativedelta(days=1)
                domain.extend([('date', '>=', date_start), ('date', '<=', date_end)])
                balance_domain.append(('invoice_date', '<', date_start))
            elif data_range == 'last-quarter':
                date_start = previous_quarter_start
                domain.extend([('date', '>=', date_start), ('date', '<=', previous_quarter_end)])
                balance_domain.append(('invoice_date', '<', date_start))
            elif 'start_date' in data_range and 'end_date' in data_range:
                date_start = datetime.strptime(data_range['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(data_range['end_date'], '%Y-%m-%d').date()
                domain.extend([('date', '>=', date_start), ('date', '<=', end_date)])
                balance_domain.append(('invoice_date', '<', date_start))
            elif 'start_date' in data_range:
                date_start = datetime.strptime(data_range['start_date'], '%Y-%m-%d').date()
                domain.append(('date', '>=', date_start))
                balance_domain.append(('invoice_date', '<', date_start))
            elif 'end_date' in data_range:
                end_date = datetime.strptime(data_range['end_date'], '%Y-%m-%d').date()
                domain.append(('date', '<=', end_date))
                fiscal_year = self.env['res.company'].search([]).mapped('account_opening_date')[0].strftime('%Y-%m-%d')
                date_start = datetime.strptime(fiscal_year, '%Y-%m-%d').date()
                balance_domain.append(('invoice_date', '<', date_start))

        # OPTIMIZATION: One read_group query for all partners
        move_lines_grouped = self.env['account.move.line'].read_group(
            domain, ['partner_id', 'debit', 'credit'], ['partner_id']
        )
        totals_map = {r['partner_id'][0]: {'debit': r['debit'], 'credit': r['credit']} for r in move_lines_grouped if r['partner_id']}

        # Initial balance query
        init_move_lines = []
        if date_start:
            init_move_lines = self.env['account.move.line'].read_group(
                balance_domain, ['partner_id', 'debit', 'credit'], ['partner_id']
            )
        init_totals_map = {r['partner_id'][0]: {'debit': r['debit'], 'credit': r['credit']} for r in init_move_lines if r['partner_id']}

        currency_id = self.env.company.currency_id.symbol
        partner_recs = self.env['res.partner'].browse(partner_id)
        partner_names = {p.id: p.name for p in partner_recs}

        for p_id in partner_id:
            p_name = partner_names.get(p_id, 'Unknown')
            t_debit = totals_map.get(p_id, {}).get('debit', 0.0)
            t_credit = totals_map.get(p_id, {}).get('credit', 0.0)

            init_debit = init_totals_map.get(p_id, {}).get('debit', 0.0)
            init_credit = init_totals_map.get(p_id, {}).get('credit', 0.0)
            init_balance = init_debit - init_credit

            partner_dict[p_name] = [] # Empty list for lazy loading
            partner_totals[p_name] = {
                'total_debit': round(t_debit, 2),
                'total_credit': round(t_credit, 2),
                'currency_id': currency_id,
                'partner_id': p_id,
                'initial_balance': init_balance,
                'move_name': 'Initial Balance',
                'initial_debit': init_debit,
                'initial_credit': init_credit,
            }

        partner_dict['partner_totals'] = partner_totals
        return partner_dict



    @api.model
    def get_partner_lines(self, partner_id, data_range, account, options, account_ids=None):
        """
        Devuelve los apuntes de UN tercero, bajo demanda.

        Metodo anadido por MBA Consultings, no existe en el modulo original de
        Cybrosys. Lo invoca ``static/src/js/partner_ledger.js`` cuando el
        usuario despliega un tercero en la pantalla del reporte, de modo que la
        carga inicial solo trae totales agregados.

        :param partner_id: Id del tercero cuyos apuntes se solicitan.
        :type partner_id: int
        :param data_range: Rango de fechas, mismo formato que en
            ``get_filter_values``.
        :type data_range: str or dict
        :param account: Tipos de cuenta a incluir ('Receivable', 'Payable').
        :type account: list or str
        :param options: Si incluye 'draft', suma los asientos en borrador.
        :type options: dict
        :param account_ids: Cuentas concretas por las que filtrar.
        :return: Lista de apuntes, cada uno enriquecido con el codigo de cuenta
            (``code``) y el codigo de diario (``jrnl``).
        :rtype: list
        """
        if options == {}: options = None
        if account == {}: account = None
        account_type_domain = []
        if options is None:
            option_domain = ['posted']
        elif 'draft' in options:
            option_domain = ['posted', 'draft']

        if account is None or ('Receivable' in account and 'Payable' in account):
            account_type_domain.extend(['liability_payable', 'asset_receivable'])
        elif 'Receivable' in account:
            account_type_domain.append('asset_receivable')
        elif 'Payable' in account:
            account_type_domain.append('liability_payable')

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        previous_quarter_start = quarter_start - relativedelta(months=3)
        previous_quarter_end = quarter_start - relativedelta(days=1)

        base_domain = [
            ('partner_id', '=', partner_id),
            ('account_type', 'in', account_type_domain),
            ('parent_state', 'in', option_domain)
        ]
        if account_ids:
            base_domain.append(('account_id', 'in', account_ids))

        if data_range:
            if data_range == 'month':
                domain = base_domain + [
                    ('date', '>=', fields.Date.today().replace(day=1)),
                    ('date', '<=', fields.Date.today())
                ]
                move_line_ids = self.env['account.move.line'].search(domain).filtered(
                    lambda x: x.date.month == fields.Date.today().month)
            elif data_range == 'year':
                move_line_ids = self.env['account.move.line'].search(base_domain).filtered(
                    lambda x: x.date.year == fields.Date.today().year)
            elif data_range == 'quarter':
                move_line_ids = self.env['account.move.line'].search(base_domain + [
                    ('date', '>=', quarter_start),
                    ('date', '<=', quarter_end)])
            elif data_range == 'last-month':
                move_line_ids = self.env['account.move.line'].search(base_domain).filtered(
                    lambda x: x.date.month == fields.Date.today().month - 1)
            elif data_range == 'last-year':
                move_line_ids = self.env['account.move.line'].search(base_domain).filtered(
                    lambda x: x.date.year == fields.Date.today().year - 1)
            elif data_range == 'last-quarter':
                move_line_ids = self.env['account.move.line'].search(base_domain + [
                    ('date', '>=', previous_quarter_start),
                    ('date', '<=', previous_quarter_end)])
            elif 'start_date' in data_range and 'end_date' in data_range:
                start_date = datetime.strptime(data_range['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(data_range['end_date'], '%Y-%m-%d').date()
                move_line_ids = self.env['account.move.line'].search(base_domain + [
                    ('date', '>=', start_date),
                    ('date', '<=', end_date)])
            elif 'start_date' in data_range:
                start_date = datetime.strptime(data_range['start_date'], '%Y-%m-%d').date()
                move_line_ids = self.env['account.move.line'].search(base_domain + [
                    ('date', '>=', start_date)])
            elif 'end_date' in data_range:
                end_date = datetime.strptime(data_range['end_date'], '%Y-%m-%d').date()
                move_line_ids = self.env['account.move.line'].search(base_domain + [
                    ('date', '<=', end_date)])
        else:
            move_line_ids = self.env['account.move.line'].search(base_domain)

        move_line_list = []
        for move_line in move_line_ids:
            move_line_data = move_line.read(
                ['date', 'move_name', 'account_type', 'debit', 'credit',
                 'date_maturity', 'account_id', 'journal_id', 'move_id',
                 'matching_number', 'amount_currency'])
            account_code = self.env['account.account'].browse(
                move_line.account_id.id).code
            journal_code = self.env['account.journal'].browse(
                move_line.journal_id.id).code
            if account_code:
                move_line_data[0]['jrnl'] = journal_code
                move_line_data[0]['code'] = account_code
            move_line_list.append(move_line_data)

        return move_line_list

    @api.model
    def get_xlsx_report(self, data, response, report_name, report_action):
        """
        Generate an Excel report based on the provided data.

        :param data: The data used to generate the report.
        :type data: str (JSON format)

        :param response: The response object to write the report to.
        :type response: object

        :param report_name: The name of the report.
        :type report_name: str

        :return: None
        """
        data = json.loads(data)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        start_date = data['filters']['start_date'] if data['filters']['start_date'] else ''
        end_date = data['filters']['end_date'] if data['filters']['end_date'] else ''
        sheet = workbook.add_worksheet()

        # Define formats
        head = workbook.add_format({'font_size': 15, 'align': 'center', 'bold': True})
        head_highlight = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        sub_heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px', 'border': 1, 'bg_color': '#D3D3D3',
             'border_color': 'black'})
        filter_head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px', 'border': 1, 'bg_color': '#D3D3D3',
             'border_color': 'black'})
        filter_body = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        side_heading_sub = workbook.add_format(
            {'align': 'left', 'bold': True, 'font_size': '10px', 'border': 1, 'border_color': 'black'})
        side_heading_sub.set_indent(1)
        txt_name = workbook.add_format({'font_size': '10px', 'border': 1})
        txt_name.set_indent(2)

        # Set column widths
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)

        # Write headers and filters
        col = 0
        sheet.write('A1:B1', report_name, head)
        sheet.write('B3:B4', 'Date Range', filter_head)
        sheet.write('B4:B4', 'Partners', filter_head)
        sheet.write('B5:B4', 'Accounts', filter_head)
        sheet.write('B6:B4', 'Options', filter_head)

        if start_date or end_date:
            sheet.merge_range('C3:G3', f"{start_date} to {end_date}", filter_body)

        if data['filters']['partner']:
            display_names = [partner.get('display_name', 'undefined') for partner in data['filters']['partner']]
            display_names_str = ', '.join(display_names)
            sheet.merge_range('C4:G4', display_names_str, filter_body)

        if data['filters']['account']:
            account_keys = list(data['filters']['account'].keys())
            account_keys_str = ', '.join(account_keys)
            sheet.merge_range('C5:G5', account_keys_str, filter_body)

        if data['filters']['options']:
            option_keys = list(data['filters']['options'].keys())
            option_keys_str = ', '.join(option_keys)
            sheet.merge_range('C6:G6', option_keys_str, filter_body)

        # Define a helper function to format numbers with thousand separators
        def format_number(value):
            if value is None:
                return "0.00"
            return "{:,.2f}".format(float(value))

        # Process partner data
        if data and report_action == 'dynamic_accounts_report.action_partner_ledger':
            sheet.write(8, col, ' ', sub_heading)
            sheet.write(8, col + 1, 'JNRL', sub_heading)
            sheet.write(8, col + 2, 'Account', sub_heading)
            sheet.merge_range('D9:E9', 'Ref', sub_heading)
            sheet.merge_range('F9:G9', 'Due Date', sub_heading)
            sheet.merge_range('H9:I9', 'Debit', sub_heading)
            sheet.merge_range('J9:K9', 'Credit', sub_heading)
            sheet.merge_range('L9:M9', 'Balance', sub_heading)

            row = 8
            # Ensure data['partners'] is iterable; default to empty list if None
            partners = data.get('partners', []) or []
            for partner in partners:
                row += 1
                # Format partner totals
                total_debit = data['total'][partner]['total_debit'] if data['total'] and partner in data['total'] else 0
                total_credit = data['total'][partner]['total_credit'] if data['total'] and partner in data[
                    'total'] else 0
                balance = total_debit - total_credit

                sheet.write(row, col, partner, txt_name)
                sheet.write(row, col + 1, ' ', txt_name)
                sheet.write(row, col + 2, ' ', txt_name)
                sheet.merge_range(row, col + 3, row, col + 4, ' ', txt_name)
                sheet.merge_range(row, col + 5, row, col + 6, ' ', txt_name)
                sheet.merge_range(row, col + 7, row, col + 8, format_number(total_debit), txt_name)
                sheet.merge_range(row, col + 9, row, col + 10, format_number(total_credit), txt_name)
                sheet.merge_range(row, col + 11, row, col + 12, format_number(balance), txt_name)

                # Handle initial balance
                initial_balance = data['total'][partner]['initial_balance'] if data['total'] and partner in data[
                    'total'] else 0
                if initial_balance != 0:
                    row += 1
                    initial_debit = data['total'][partner]['initial_debit'] if data['total'] and partner in data[
                        'total'] else 0
                    initial_credit = data['total'][partner]['initial_credit'] if data['total'] and partner in data[
                        'total'] else 0

                    sheet.write(row, col, '', txt_name)
                    sheet.write(row, col + 1, ' ', txt_name)
                    sheet.write(row, col + 2, ' ', txt_name)
                    sheet.merge_range(row, col + 3, row, col + 4, 'Initial Balance', head_highlight)
                    sheet.merge_range(row, col + 5, row, col + 6, ' ', txt_name)
                    sheet.merge_range(row, col + 7, row, col + 8, format_number(initial_debit), txt_name)
                    sheet.merge_range(row, col + 9, row, col + 10, format_number(initial_credit), txt_name)
                    sheet.merge_range(row, col + 11, row, col + 12, format_number(initial_balance), txt_name)

                # Process move lines for the partner
                for rec in data['data'][partner]:
                    row += 1
                    sheet.write(row, col, rec[0]['date'], txt_name)
                    sheet.write(row, col + 1, rec[0]['jrnl'], txt_name)
                    sheet.write(row, col + 2, rec[0]['code'], txt_name)
                    sheet.merge_range(row, col + 3, row, col + 4, rec[0]['move_name'], txt_name)
                    sheet.merge_range(row, col + 5, row, col + 6, rec[0]['date_maturity'] or '', txt_name)
                    sheet.merge_range(row, col + 7, row, col + 8, format_number(rec[0]['debit']), txt_name)
                    sheet.merge_range(row, col + 9, row, col + 10, format_number(rec[0]['credit']), txt_name)
                    sheet.merge_range(row, col + 11, row, col + 12, ' ', txt_name)

            # Grand totals
            row += 1
            # Ensure grand_total values are numbers
            grand_total_debit = data['grand_total']['total_debit'] if data['grand_total'] and data['grand_total'][
                'total_debit'] is not None else 0
            grand_total_credit = data['grand_total']['total_credit'] if data['grand_total'] and data['grand_total'][
                'total_credit'] is not None else 0
            grand_balance = grand_total_debit - grand_total_credit

            sheet.merge_range(row, col, row, col + 6, 'Total', filter_head)
            sheet.merge_range(row, col + 7, row, col + 8, format_number(grand_total_debit), filter_head)
            sheet.merge_range(row, col + 9, row, col + 10, format_number(grand_total_credit), filter_head)
            sheet.merge_range(row, col + 11, row, col + 12, format_number(grand_balance), filter_head)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


