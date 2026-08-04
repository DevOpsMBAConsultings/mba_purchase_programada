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
    Parser agnóstico para lectura de cotizaciones en PDF.
    Extrae la cabecera (cliente, fecha, vendedor, número, términos de pago),
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

        text = doc[0].get_text('text')
        blocks = doc[0].get_text('blocks')

        # 1. Búsqueda de bloques de cabecera por coordenadas y texto
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

        # 2. Cliente (Partner) - El bloque inferior a 'Cotizado a:'
        customer_name = None
        if cotizado_b:
            for b in blocks:
                if b != cotizado_b and abs(b[1] - cotizado_b[3]) < 25 and 150 < b[0] < 300:
                    customer_name = b[4].split('\n')[0].strip()
                    break

        if not customer_name:
            # Fallback por regex si cambia la posición en la plantilla
            c_m = re.search(r'Cotizado a:\s*\n([^\n]+)', text)
            if c_m:
                customer_name = c_m.group(1).strip()

        # 3. Forma de Pago
        payment_term = 'CREDITO'
        if fp_block:
            for b in blocks:
                if b != fp_block and abs(b[1] - fp_block[3]) < 15 and 200 < b[0] < 350:
                    val = b[4].strip()
                    if val:
                        payment_term = val
                    break

        # 4. Vendedor
        salesperson = None
        if vend_block:
            for b in blocks:
                if b != vend_block and abs(b[1] - vend_block[3]) < 15 and b[0] > 380:
                    val = b[4].strip()
                    if val:
                        salesperson = val
                    break

        # 5. Número de Cotización
        q_num = None
        q_match = re.search(r'\n(\d{4,})\nFECHA:', text)
        if not q_match:
            q_match = re.search(r'COTIZACI[OÓ]N\s*[:#]?\s*([A-Za-z0-9\-_]*\d+[A-Za-z0-9\-_]*)', text, re.IGNORECASE)
        if q_match:
            q_num = q_match.group(1).strip()

        # 6. Fecha de Cotización
        date_order = fields_date_today()
        d_match = re.search(r'FECHA:\s*([^\n]+)', text)
        if d_match:
            date_str = d_match.group(1).strip()
            # Mapeo de formatos comunes (ej. 'Aug 3, 2026', '03/08/2026', '2026-08-03')
            for fmt in ('%b %d, %Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    date_order = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue

        # 7. Totales (Subtotal, ITBMS, Total)
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

        # 8. Líneas de Artículo (Cantidad, Código, Descripción, Impuesto, Precio, Monto)
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

        doc.close()

        return {
            'quotation_number': q_num,
            'date_order': date_order,
            'customer_name': customer_name,
            'payment_term': payment_term,
            'salesperson': salesperson,
            'subtotal': subtotal_val,
            'itbms': itbms_val,
            'total': total_val,
            'lines': lines,
        }


def fields_date_today():
    return datetime.today().strftime('%Y-%m-%d')
