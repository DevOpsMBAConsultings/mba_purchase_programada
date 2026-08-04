# -*- coding: utf-8 -*-
import base64
import os
from odoo.tests.common import TransactionCase, tagged
from ..wizard.pdf_parser import QuotationPDFParser


@tagged('post_install', '-at_install')
class TestPdfQuotationImport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sample_dir = os.path.join(os.path.dirname(__file__), 'sample_pdfs')
        cls.pdf_54345 = os.path.join(cls.sample_dir, '54345.pdf')
        cls.pdf_54346 = os.path.join(cls.sample_dir, '54346.pdf')

    def test_01_parse_pdf_54345(self):
        """Valida que el parser extraiga correctamente la cotización 54345 de SERVIESTIBA S.A."""
        if not os.path.exists(self.pdf_54345):
            self.skipTest('Archivo de muestra 54345.pdf no encontrado.')

        with open(self.pdf_54345, 'rb') as f:
            pdf_bytes = f.read()

        res = QuotationPDFParser.parse_pdf_bytes(pdf_bytes, '54345.pdf')
        self.assertEqual(res['quotation_number'], '54345')
        self.assertEqual(res['customer_name'], 'SERVIESTIBA S.A.')
        self.assertEqual(len(res['lines']), 21)
        self.assertAlmostEqual(res['total'], 1008.09, places=2)
        self.assertAlmostEqual(res['subtotal'], 942.14, places=2)

    def test_02_parse_pdf_54346(self):
        """Valida extracción e impuestos exentos ('EX') en la cotización 54346 de SIMPOL, S.A."""
        if not os.path.exists(self.pdf_54346):
            self.skipTest('Archivo de muestra 54346.pdf no encontrado.')

        with open(self.pdf_54346, 'rb') as f:
            pdf_bytes = f.read()

        res = QuotationPDFParser.parse_pdf_bytes(pdf_bytes, '54346.pdf')
        self.assertEqual(res['quotation_number'], '54346')
        self.assertEqual(res['customer_name'], 'SIMPOL, S.A.')
        self.assertEqual(len(res['lines']), 18)
        self.assertAlmostEqual(res['total'], 157.41, places=2)

        # Verificar que los primeros 3 productos (CREMORA, CAFE, AGUA) se detectaron exentos
        self.assertTrue(res['lines'][0]['tax_exempt'])
        self.assertTrue(res['lines'][1]['tax_exempt'])
        self.assertTrue(res['lines'][2]['tax_exempt'])

    def test_03_wizard_import_creates_order(self):
        """Valida la importación vía Wizard, asignación a Consumidor Final si el cliente falta, y líneas en borrador."""
        if not os.path.exists(self.pdf_54345):
            self.skipTest('Archivo de muestra 54345.pdf no encontrado.')

        with open(self.pdf_54345, 'rb') as f:
            pdf_bytes = f.read()

        attachment = self.env['ir.attachment'].create({
            'name': '54345.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_bytes),
        })

        wizard = self.env['sale.order.import.pdf.wizard'].create({
            'attachment_ids': [(6, 0, attachment.ids)],
        })

        action = wizard.action_import_pdf()
        order_id = action.get('res_id')
        self.assertTrue(order_id, 'Debe devolver el ID del pedido creado.')

        order = self.env['sale.order'].browse(order_id)
        self.assertTrue(order.imported_from_pdf)
        self.assertEqual(order.legacy_quotation_number, '54345')
        self.assertEqual(len(order.order_line), 21)

        # Como SERVIESTIBA S.A. no estaba creado previamente, debe asignar a Consumidor Final y encender alertas
        self.assertEqual(order.partner_id.name, 'Consumidor Final')
        self.assertTrue(order.has_import_warnings)
        self.assertIn('SERVIESTIBA S.A.', order.origin_customer_name)
