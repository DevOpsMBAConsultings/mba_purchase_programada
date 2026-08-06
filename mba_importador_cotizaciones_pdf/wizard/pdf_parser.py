# -*- coding: utf-8 -*-
import io
import re
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class QuotationPDFParser:
    """
    Parser agnóstico para lectura de cotizaciones y facturas electrónicas (CAFE DGI/HKA) en PDF.
    Extrae la cabecera (cliente, RUC/DV, fecha, vendedor, número, términos de pago),
    líneas de detalle (cantidad, código, descripción, impuesto, precio, subtotal)
    y totales del documento PDF.
    """

    @classmethod
    def parse_pdf_bytes(cls, pdf_bytes, filename='document.pdf'):
        if not fitz:
            raise ImportError("La librería 'PyMuPDF' (fitz) es requerida para el análisis local de archivos PDF.")

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if not doc or len(doc) == 0:
            raise ValueError(f"El archivo PDF {filename} está vacío o no se puede leer.")

        full_text = ""
        all_blocks = []
        for page in doc:
            full_text += page.get_text('text') + "\n"
            all_blocks.extend(page.get_text('blocks'))

        # Detectar si es un Comprobante Auxiliar de Factura Electrónica (CAFE) DGI/HKA
        is_cafe = 'Comprobante Auxiliar' in full_text or 'DGI' in full_text or 'FE01' in filename or 'FE04' in filename or 'Protocolo de autorización' in full_text

        if is_cafe:
            res = cls._parse_cafe_pdf(doc, full_text, all_blocks, filename=filename)
        else:
            res = cls._parse_quotation_pdf(doc, full_text, all_blocks, filename=filename)

        doc.close()
        return res

    @classmethod
    def _parse_cafe_pdf(cls, doc, full_text, all_blocks, filename=''):
        rec_name = None
        rec_ruc = None
        rec_dv = None

        for b in all_blocks:
            b_text = b[4]
            if 'Nombre:' in b_text:
                lines = [l.strip() for l in b_text.split('\n') if l.strip()]
                for l in lines:
                    if 'Nombre:' in l and 'SIMPLIFICA' not in l.upper():
                        rec_name = l.replace('Nombre:', '').strip()
            if 'RUC:' in b_text:
                rucs = re.findall(r'RUC:\s*\n?\s*([0-9\-_A-Za-z]+)', b_text)
                dvs = re.findall(r'DV:\s*\n?\s*([0-9A-Za-z]+)', b_text)
                if len(rucs) >= 2:
                    rec_ruc = rucs[1]
                    if len(dvs) >= 2:
                        rec_dv = dvs[1]
                elif len(rucs) == 1 and '1607293' not in rucs[0]:
                    rec_ruc = rucs[0]
                    if len(dvs) >= 1:
                        rec_dv = dvs[0]

        num_m = re.search(r'N[uú]mero:\s*\n?\s*(\d+)', full_text, re.IGNORECASE)
        q_num = num_m.group(1) if num_m else None

        date_order = fields_date_today()
        date_m = re.search(r'(\d{1,2})\s+de\s+([A-Za-z]+)\s+de\s+(\d{4})', full_text, re.IGNORECASE)
        months = {'enero':'01','febrero':'02','marzo':'03','abril':'04','mayo':'05','junio':'06','julio':'07','agosto':'08','septiembre':'09','octubre':'10','noviembre':'11','diciembre':'12'}
        if date_m:
            d = date_m.group(1).zfill(2)
            m = months.get(date_m.group(2).lower(), '01')
            y = date_m.group(3)
            date_order = f'{y}-{m}-{d}'

        doc_type = 'out_refund' if ('Nota de crédito' in full_text or (filename and 'FE04' in filename)) else 'out_invoice'

        def _parse_float(match):
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    return 0.0
            return 0.0

        subtotal_val = _parse_float(re.search(r'Subtotal\s*sin\s*impuestos\s*([\d\.,]+)', full_text, re.IGNORECASE))
        itbms_val = _parse_float(re.search(r'Impuestos\s*([\d\.,]+)', full_text, re.IGNORECASE))
        total_val = _parse_float(re.search(r'Total\s*([\d\.,]+)', full_text, re.IGNORECASE))

        lines = []
        for b in all_blocks:
            b_text = b[4]
            lines_b = [l.strip() for l in b_text.split('\n') if l.strip()]
            if lines_b and lines_b[0].isdigit() and len(lines_b) >= 6:
                code = lines_b[1]
                desc = lines_b[2]
                try:
                    qty = float(lines_b[3].replace(',', ''))
                    price_unit = float(lines_b[5].replace(',', ''))
                except ValueError:
                    continue
                is_exempt = '(E)' in desc or '(EX)' in desc
                lines.append({
                    'code': code,
                    'description': desc,
                    'qty': qty,
                    'price_unit': price_unit,
                    'tax_exempt': is_exempt,
                    'amount': qty * price_unit,
                })

        return {
            'quotation_number': q_num,
            'date_order': date_order,
            'customer_name': rec_name,
            'customer_ruc': rec_ruc,
            'customer_dv': rec_dv,
            'doc_type': doc_type,
            'payment_term': 'CREDITO',
            'salesperson': None,
            'subtotal': subtotal_val,
            'itbms': itbms_val,
            'total': total_val,
            'lines': lines,
        }

    @classmethod
    def _parse_quotation_pdf(cls, doc, text, blocks, filename=''):
        cotizado_b = None
        fp_block = None
        vend_block = None
        for b in blocks:
            text_block = b[4]
            if 'Cotizado a:' in text_block or 'Cotizado a' in text_block:
                cotizado_b = b
            if 'Forma de pago' in text_block:
                fp_block = b
            if 'Vendedor' in text_block:
                vend_block = b

        customer_name = None
        if cotizado_b:
            for b in blocks:
                if b != cotizado_b and abs(b[1] - cotizado_b[3]) < 25 and 150 < b[0] < 300:
                    customer_name = b[4].split('\n')[0].strip()
                    break

        if not customer_name:
            c_m = re.search(r'Cotizado a:\s*\n([^\n]+)', text)
            if c_m:
                customer_name = c_m.group(1).strip()

        payment_term = 'CREDITO'
        if fp_block:
            for b in blocks:
                if b != fp_block and abs(b[1] - fp_block[3]) < 15 and 200 < b[0] < 350:
                    val = b[4].strip()
                    if val:
                        payment_term = val
                    break

        salesperson = None
        if vend_block:
            for b in blocks:
                if b != vend_block and abs(b[1] - vend_block[3]) < 15 and b[0] > 380:
                    val = b[4].strip()
                    if val:
                        salesperson = val
                    break

        q_num = None
        q_match = re.search(r'\n(\d{4,})\nFECHA:', text)
        if not q_match:
            q_match = re.search(r'COTIZACI[OÓ]N\s*[:#]?\s*([A-Za-z0-9\-_]*\d+[A-Za-z0-9\-_]*)', text, re.IGNORECASE)
        if q_match:
            q_num = q_match.group(1).strip()

        date_order = fields_date_today()
        d_match = re.search(r'FECHA:\s*([^\n]+)', text)
        if d_match:
            date_str = d_match.group(1).strip()
            for fmt in ('%b %d, %Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    date_order = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue

        def _parse_float(match):
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    return 0.0
            return 0.0

        subtotal_val = _parse_float(re.search(r'Subtotal\s*([\d\.,]+)', text, re.IGNORECASE))
        itbms_val = _parse_float(re.search(r'I\.T\.B\.M\.S\.\s*([\d\.,]+)', text, re.IGNORECASE))
        total_val = _parse_float(re.search(r'TOTAL\s*([\d\.,]+)', text, re.IGNORECASE))

        lines = []
        pattern = re.compile(
            r'^(\d+\.\d{2})\s+([A-Za-z0-9\-_]+)\s*\n'
            r'([^\n]+)\s*\n'
            r'(?:(EX)\s*\n)?'
            r'(\d+\.\d{2})\s*\n'
            r'(\d+\.\d{2})',
            re.MULTILINE
        )

        for m in pattern.finditer(text):
            lines.append({
                'qty': float(m.group(1)),
                'code': m.group(2).strip(),
                'description': m.group(3).strip(),
                'tax_exempt': bool(m.group(4)),
                'price_unit': float(m.group(5)),
                'amount': float(m.group(6)),
            })

        return {
            'quotation_number': q_num,
            'date_order': date_order,
            'customer_name': customer_name,
            'customer_ruc': None,
            'customer_dv': None,
            'doc_type': 'out_invoice',
            'payment_term': payment_term,
            'salesperson': salesperson,
            'subtotal': subtotal_val,
            'itbms': itbms_val,
            'total': total_val,
            'lines': lines,
        }


def fields_date_today():
    return datetime.today().strftime('%Y-%m-%d')
