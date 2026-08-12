# -*- coding: utf-8 -*-
import requests
import json
import logging
import re
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HKAClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        
    def _clean_location_name(self, text):
        if not text:
            return ""
        return text.strip()
        

    def build_payload(self, invoice):
        """
        Construye el JSON requerido por la API REST de HKA (endpoint: /api/Enviar).
        Estructura según documentación oficial HKA:
        - listaItems y totalesSubTotales van a nivel de 'documento' (NO dentro de datosTransaccion)
        - tasaITBMS y valorITBMS son campos PLANOS en cada item (NO en array 'itbms')
        - El campo total del item se llama 'valorTotal' (NO 'valorTotalItem')
        """
        journal_sucursal = invoice.journal_id.l10n_pa_sucursal_code
        company_sucursal = invoice.company_id.l10n_pa_sucursal_code
        codigo_sucursal = (journal_sucursal or company_sucursal or "0000").zfill(4)

        journal_pto = invoice.journal_id.l10n_pa_pto_fact_df
        company_pto = invoice.company_id.l10n_pa_pto_fact
        punto_facturacion = (journal_pto or company_pto or "001").zfill(3)

        # Solo líneas de producto (excluir secciones, notas, líneas de impuesto y redondeo)
        valid_lines = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type not in ('line_section', 'line_note', 'tax', 'rounding')
                      and not getattr(l, 'is_rounding_line', False)
        )
        contact_partner = invoice.partner_id
        commercial_partner = invoice.commercial_partner_id or contact_partner
        # Siempre buscar la verdadera casa matriz (top-level parent) para datos fiscales
        # Esto soluciona el caso donde el usuario crea una sucursal como "Empresa"
        while commercial_partner.parent_id:
            commercial_partner = commercial_partner.parent_id

        # Usamos los campos snapshot de la factura para consistencia
        tipo_cliente = getattr(invoice, "dgi_partner_receptor_tipo", None) or getattr(commercial_partner, "l10n_pa_receptor_tipo", None) or "02"
        partner_ruc = getattr(invoice, "dgi_partner_ruc", None) or getattr(commercial_partner, "l10n_pa_ruc", None) or commercial_partner.vat or ""
        partner_ruc = (partner_ruc or "").strip()
        partner_dv = getattr(invoice, "dgi_partner_dv", None) or getattr(commercial_partner, "l10n_pa_dv", None) or ""

        # HKA valida numeroRUC contra el formato de RUC/cédula panameña (error 109) y rechaza
        # TANTO "CF" ("El campo numeroRUC es inválido") COMO el valor vacío/ausente
        # ("El campo numeroRUC debe ser informado") — verificado con 4 pruebas reales vs HKA demo.
        # Consumidor Final (02) = venta sin identificar al comprador: cuando el partner NO tiene una
        # cédula/RUC real capturado (vacío, None, "CF" o cualquier placeholder sin dígitos), HKA
        # acepta el comodín "00000". Nunca se inventa una cédula real; si el partner SÍ tiene una
        # cédula real (con dígitos), se envía tal cual sin tocar.
        # "CF" es la convención interna de CF sin RUC (res_partner fuerza vat="CF"), no un RUC real.
        # NOTA: Digifact resuelve este mismo caso enviando el campo VACÍO (regla XSD DGI distinta);
        # esa lógica es exclusiva de Digifact y NO se comparte — la API REST de HKA exige "00000".
        if tipo_cliente == "02":
            # HKA valida numeroRUC contra el formato numérico de RUC/cédula panameña (error 109).
            # Si el RUC viene con prefijos como "PN-", "PE-", "CF", letras o no es una cédula numérica limpia,
            # para Consumidor Final (02) se envía el comodín "00000" aceptado oficialmente por HKA.
            is_valid_numeric_ruc = bool(re.match(r"^(\d{1,2}-\d{1,5}-\d{1,6}|\d{1,2}-NT-\d{1,5}-\d{1,6}|\d{7,15})$", partner_ruc))
            if not partner_ruc or partner_ruc.upper() == "CF" or not is_valid_numeric_ruc:
                partner_ruc = "00000"
                partner_dv = ""
        partner_name = getattr(invoice, "dgi_partner_name", None) or commercial_partner.name or ""
        partner_taxpayer_type = getattr(invoice, "dgi_partner_taxpayer_type", None) or getattr(commercial_partner, "l10n_pa_tipo_contribuyente", None) or ("2" if commercial_partner.company_type == "company" else "1")

        # --- Datos del Cliente ---
        cliente_data = {
            "tipoClienteFE": tipo_cliente,
            "numeroRUC": partner_ruc,
            "digitoVerificadorRUC": partner_dv,
            "razonSocial": partner_name,
            "direccion": commercial_partner.street or "Panama",
            "codigoUbicacion": commercial_partner.l10n_pa_corregimiento_id.code if (tipo_cliente != "04" and commercial_partner.l10n_pa_corregimiento_id) else ("1-1-1" if tipo_cliente != "04" else ""),
            "provincia": self._clean_location_name(commercial_partner.l10n_pa_provincia_id.name) if tipo_cliente != "04" else "",
            "distrito": self._clean_location_name(commercial_partner.l10n_pa_distrito_id.name) if tipo_cliente != "04" else "",
            "corregimiento": self._clean_location_name(commercial_partner.l10n_pa_corregimiento_id.name) if tipo_cliente != "04" else "",
            "telefono1": __import__("re").sub(r"^\+507\s*", "", contact_partner.phone or commercial_partner.phone or "").replace("+", "").strip()[:20],
            "correoElectronico1": contact_partner.email or commercial_partner.email or "",
            "pais": commercial_partner.country_id.code or "PA",
        }

        if tipo_cliente != "04":
            cliente_data["tipoContribuyente"] = partner_taxpayer_type

        if tipo_cliente == "04":
            # Extranjero: campos de identificación extranjera
            tipo_id = getattr(commercial_partner, 'l10n_pa_tipo_identificacion', None) or "01"
            cliente_data["tipoIdentificacion"] = tipo_id
            cliente_data["nroIdentificacionExtranjero"] = commercial_partner.vat or ""
            cliente_data["paisExtranjero"] = commercial_partner.country_id.name or ""
            # Para extranjero pais no puede ser PA si destino es extranjero
            if (commercial_partner.country_id.code or "PA") == "PA":
                cliente_data["pais"] = "US"  # fallback razonable

        # --- Forma y Tiempo de Pago ---
        # tiempoPago: 1=Inmediato(contado), 2=Plazo(crédito)
        tiempo_pago = "2" if getattr(invoice, "dgi_payment_term_type", "contado") == "credito" else "1"
        # formaPagoFact: 01=Crédito si es a plazo; si no, usar el método configurado
        forma_pago_code = (getattr(invoice.dgi_payment_method_id, "code", None) or "02") if getattr(invoice, "dgi_payment_method_id", None) else "02"
        forma_pago = "01" if tiempo_pago == "2" else forma_pago_code

        # --- Estructura base del totalesSubTotales ---
        # Los totales ITBMS se recalculan DESPUÉS del loop de items
        # para que totalITBMS == suma de valorITBMS de los items (validación HKA)
        totales_sub_totales = {
            "totalPrecioNeto": f"{round(invoice.amount_untaxed, 2):.2f}",
            "totalITBMS": "0.00",  # se recalcula después
            "totalMontoGravado": "0.00",  # se recalcula después
            "totalFactura": "0.00",  # se recalcula después
            "totalValorRecibido": "0.00",  # se recalcula después
            "tiempoPago": tiempo_pago,
            "nroItems": str(len(valid_lines)),
            "totalTodosItems": "0.00",  # se recalcula después
            "listaFormaPago": [
                {
                    "formaPagoFact": forma_pago,
                    "valorCuotaPagada": f"{round(invoice.amount_total, 2):.2f}"
                }
            ]
        }

        # --- Detección de Nota de Crédito (ANTES de listaPagoPlazo) ---
        is_credit_note = invoice.move_type == 'out_refund'
        original_invoice = getattr(invoice, 'reversed_entry_id', None)
        is_referenced = bool(original_invoice and getattr(original_invoice, 'l10n_pa_cufe', None))

        if is_credit_note:
            if is_referenced:
                tipo_documento = "04"  # NC Referenciada
            else:
                tipo_documento = "06"  # NC Genérica
            tipo_venta = ""  # No aplica para NC
            # tiempoPago: 3 = No aplica (Nota de Crédito)
            totales_sub_totales["tiempoPago"] = "3"
            # NC con tiempoPago "3" requiere listaPagoPlazo CON infoPagoCuota (mín 15 chars)
            totales_sub_totales["listaPagoPlazo"] = [
                {
                    "fechaVenceCuota": invoice.invoice_date.strftime(
                        "%Y-%m-%dT00:00:00-05:00"
                    ) if invoice.invoice_date else "",
                    "valorCuota": f"{round(invoice.amount_total, 2):.2f}",
                    "infoPagoCuota": "Nota de credito electronica",
                }
            ]
        else:
            tipo_documento = invoice.dgi_document_type_id.code if invoice.dgi_document_type_id else "01"
            tipo_venta = "1"  # Venta de Giro del negocio

            # listaPagoPlazo: obligatorio cuando tiempoPago == "2" (crédito/plazo)
            # Solo para facturas, NO para notas de crédito
            if tiempo_pago == "2" and invoice.invoice_date_due:
                # infoPagoCuota: DGI exige mínimo 15 caracteres y máximo 50 caracteres
                info_cuota = invoice.invoice_payment_term_id.name if invoice.invoice_payment_term_id else "Pago a plazo"
                if len(info_cuota) < 15:
                    info_cuota = info_cuota.ljust(15, " ")  # Pad con espacios hasta 15
                elif len(info_cuota) > 50:
                    info_cuota = info_cuota[:50]
                totales_sub_totales["listaPagoPlazo"] = [
                    {
                        "fechaVenceCuota": invoice.invoice_date_due.strftime("%Y-%m-%dT00:00:00-05:00"),
                        "valorCuota": f"{round(invoice.amount_total, 2):.2f}",
                        "infoPagoCuota": info_cuota
                    }
                ]

        # --- Construcción del payload completo ---
        # IMPORTANTE: listaItems y totalesSubTotales van a nivel de 'documento',
        # NO dentro de 'datosTransaccion' (documentación oficial HKA REST API)
        datos_transaccion = {
            "tipoEmision": "01",
            "tipoDocumento": tipo_documento,
            "numeroDocumentoFiscal": re.search(r'\d+$', invoice.name).group().zfill(10) if invoice.name and re.search(r'\d+$', invoice.name) else "0000000000",
            "puntoFacturacionFiscal": punto_facturacion,
            "fechaEmision": invoice.invoice_date.strftime("%Y-%m-%dT00:00:00-05:00") if invoice.invoice_date else "",
            "naturalezaOperacion": invoice.dgi_naturaleza_operacion or "01",
            "tipoOperacion": invoice.dgi_tipo_operacion or "1",
            "destinoOperacion": "1",
            "formatoCAFE": "3",
            "entregaCAFE": "1",
            "envioContenedor": "1",
            "procesoGeneracion": "1",
            "tipoVenta": tipo_venta,
            "cliente": cliente_data,
        }

        # Información de interés (notas complementarias)
        if invoice.dgi_payment_notes:
            datos_transaccion["informacionInteres"] = (invoice.dgi_payment_notes or "")[:5000]

        # --- Bloque de documento fiscal referenciado (obligatorio para NC 04) ---
        if is_credit_note and is_referenced:
            datos_transaccion["listaDocsFiscalReferenciados"] = [
                {
                    "fechaEmisionDocFiscalReferenciado": original_invoice.invoice_date.strftime(
                        "%Y-%m-%dT00:00:00-05:00"
                    ) if original_invoice.invoice_date else "",
                    "cufeFEReferenciada": original_invoice.l10n_pa_cufe or "",
                    "nroFacturaPapel": "",
                    "nroFacturaImpFiscal": "",
                }
            ]

        payload = {
            "documento": {
                "codigoSucursalEmisor": codigo_sucursal,
                "datosTransaccion": datos_transaccion,
                # listaItems y totalesSubTotales a nivel de 'documento' (NO dentro datosTransaccion)
                "listaItems": [],
                "totalesSubTotales": totales_sub_totales,
            }
        }

        # --- Build listaItems ---
        # Separar líneas regulares y líneas de descuento/recompensa (ej. Odoo Loyalty en Ventas o POS)
        def is_reward_discount_line(l):
            if l.price_unit < 0 or l.price_subtotal < 0:
                return True
            if any(getattr(sl, "is_reward_line", False) for sl in l.sale_line_ids):
                return True
            if hasattr(l, "pos_line_ids") and any(getattr(pl, "is_reward_line", False) for pl in l.pos_line_ids):
                return True
            return False

        regular_lines = valid_lines.filtered(lambda l: not is_reward_discount_line(l))
        reward_lines = valid_lines - regular_lines

        if not regular_lines:
            regular_lines = valid_lines
            reward_lines = invoice.env["account.move.line"]

        total_reward_discount = sum(abs(l.price_subtotal) for l in reward_lines)
        total_regular_subtotal = sum(l.price_subtotal for l in regular_lines)

        for line in regular_lines:
            # Producto template (campos DGI viven en template, no en variante)
            prod = line.product_id
            prod_tmpl = prod.product_tmpl_id if prod else None

            # Tasa ITBMS y porcentaje
            tasa_itbms = "00"
            tax_percent = 0.0

            fp = invoice.fiscal_position_id
            is_retention_fp = fp and 'retenci' in (fp.name or '').lower()

            if is_retention_fp and prod:
                # Retención: usar impuestos originales del producto (ITBMS puro, sin mapeo fiscal)
                original_taxes = prod.taxes_id.filtered(
                    lambda t: t.company_id == invoice.company_id and t.type_tax_use == 'sale' and t.amount > 0
                )
                for tax in original_taxes:
                    amt = round(tax.amount, 0)
                    if amt == 7:
                        tasa_itbms = "01"
                        tax_percent = 7.0
                    elif amt == 10:
                        tasa_itbms = "02"
                        tax_percent = 10.0
                    elif amt == 15:
                        tasa_itbms = "03"
                        tax_percent = 15.0
                    break
            elif line.tax_ids:
                # Caso normal: usar impuestos de la línea (aplanar grupos)
                try:
                    all_taxes = line.tax_ids.flatten_taxes_hierarchy()
                except AttributeError:
                    all_taxes = line.tax_ids
                for tax in all_taxes:
                    if tax.amount > 0:
                        amt = round(tax.amount, 0)
                        if amt == 7:
                            tasa_itbms = "01"
                            tax_percent = 7.0
                        elif amt == 10:
                            tasa_itbms = "02"
                            tax_percent = 10.0
                        elif amt == 15:
                            tasa_itbms = "03"
                            tax_percent = 15.0
                        break

            # Calcular descuento unitario total (descuento propio de línea + proporción de lealtad)
            line_subtotal = line.price_subtotal
            allocated_reward = (
                (line_subtotal / total_regular_subtotal) * total_reward_discount
                if total_regular_subtotal
                else 0.0
            )

            base_unit_disc = (
                line.price_unit - (line.price_subtotal / line.quantity)
                if line.quantity
                else 0.0
            )
            reward_unit_disc = (allocated_reward / line.quantity) if line.quantity else 0.0
            precio_descuento = base_unit_disc + reward_unit_disc

            # Precios netos del item para DGI HKA (precioItem = cantidad * (precioUnitario - precioUnitarioDescuento))
            net_unit_price = line.price_unit - precio_descuento
            precio_item = round(line.quantity * net_unit_price, 2)
            itbms_item = round(precio_item * tax_percent / 100.0, 2) if tax_percent else 0.0
            valor_total_item = round(precio_item + itbms_item, 2)

            # Usar nombre del producto sin prefijo de código [SKU]
            prod_name = prod.name if prod else (line.name or "Producto")
            item = {
                "descripcion": prod_name[:500],
                "cantidad": f"{line.quantity:.4f}",
                "precioUnitario": f"{line.price_unit:.4f}",
                "precioItem": f"{precio_item:.2f}",
                "valorTotal": f"{valor_total_item:.2f}",
                "tasaITBMS": tasa_itbms,
                "valorITBMS": f"{itbms_item:.2f}",
            }

            # Descuento: solo incluir si hay descuento real
            if precio_descuento > 0:
                item["precioUnitarioDescuento"] = f"{precio_descuento:.4f}"

            # Código del producto (SKU / Referencia interna): opcional
            if prod and prod.default_code:
                item["codigo"] = prod.default_code.strip()[:20]

            # Códigos CPBS (opcionales B2B/B2C; obligatorios Gobierno tipo 03)
            cod_abrev = ""
            cod_full = ""
            if prod_tmpl:
                cod_abrev = (getattr(prod_tmpl, "dgi_cpbs_abrev", None) or "").strip()
                if not cod_abrev and prod_tmpl.dgi_cpbs_segment_id:
                    cod_abrev = (prod_tmpl.dgi_cpbs_segment_id.code or "").strip()
                cod_full = (getattr(prod_tmpl, "dgi_cpbs_codigo", None) or "").strip()
                if not cod_full and prod_tmpl.dgi_cpbs_family_id:
                    cod_full = (prod_tmpl.dgi_cpbs_family_id.code or "").strip()

            if cod_abrev:
                item["codigoCPBSAbrev"] = cod_abrev
                if cod_full:
                    item["codigoCPBS"] = cod_full
            elif cod_full:
                item["codigoCPBSAbrev"] = cod_full[:2]
                item["codigoCPBS"] = cod_full

            # Validación obligatoria para Gobierno (tipo 03)
            if tipo_cliente == "03" and "codigoCPBSAbrev" not in item:
                prod_name = prod_tmpl.name if prod_tmpl else (line.name or "desconocido")
                raise UserError(
                    f"El producto '{prod_name}' no tiene código CPBS.\n"
                    "Para facturas a entidades de Gobierno (tipo de receptor 03) "
                    "el código CPBS es obligatorio.\n"
                    "Configure la Clasificación DGI en la ficha del producto."
                )

            # Unidad de medida DGI (opcional)
            if prod_tmpl and prod_tmpl.dgi_unidad_medida_id:
                uom_code = (prod_tmpl.dgi_unidad_medida_id.code or "").strip()
                if uom_code:
                    item["unidadMedida"] = uom_code

            payload["documento"]["listaItems"].append(item)

        # --- Recalcular totales desde los items realmente enviados ---
        sum_precio_neto = round(
            sum(float(it.get("precioItem", "0")) for it in payload["documento"]["listaItems"]), 2
        )
        sum_itbms = round(
            sum(float(it.get("valorITBMS", "0")) for it in payload["documento"]["listaItems"]), 2
        )

        # --- Reconciliación de redondeo de centavos con el ITBMS real de Odoo ---
        odoo_target_tax = round(invoice.amount_tax, 2)
        diff_tax = round(sum_itbms - odoo_target_tax, 2)

        # Si hay diferencia de 1 o 2 centavos por redondeo individual vs Odoo global,
        # ajustamos la diferencia en el último ítem con impuesto > 0 para que la suma cuadre exacta con Odoo.
        if diff_tax != 0.0 and abs(diff_tax) <= 0.05:
            for item in reversed(payload["documento"]["listaItems"]):
                current_item_tax = float(item.get("valorITBMS", "0"))
                if current_item_tax > 0:
                    adjusted_item_tax = round(current_item_tax - diff_tax, 2)
                    item["valorITBMS"] = f"{adjusted_item_tax:.2f}"
                    current_item_net = float(item.get("precioItem", "0"))
                    item["valorTotal"] = f"{round(current_item_net + adjusted_item_tax, 2):.2f}"
                    sum_itbms = odoo_target_tax
                    break

        total_factura = round(sum_precio_neto + sum_itbms, 2)

        totales_sub_totales["totalPrecioNeto"] = f"{sum_precio_neto:.2f}"
        totales_sub_totales["totalITBMS"] = f"{sum_itbms:.2f}"
        totales_sub_totales["totalMontoGravado"] = f"{sum_itbms:.2f}"
        totales_sub_totales["totalFactura"] = f"{total_factura:.2f}"
        totales_sub_totales["totalValorRecibido"] = f"{total_factura:.2f}"
        totales_sub_totales["nroItems"] = str(len(payload["documento"]["listaItems"]))
        totales_sub_totales["totalTodosItems"] = f"{total_factura:.2f}"
        # Actualizar valorCuotaPagada en listaFormaPago
        totales_sub_totales["listaFormaPago"][0]["valorCuotaPagada"] = f"{total_factura:.2f}"
        # Actualizar valorCuota en listaPagoPlazo si existe
        if "listaPagoPlazo" in totales_sub_totales:
            totales_sub_totales["listaPagoPlazo"][0]["valorCuota"] = f"{total_factura:.2f}"

        # --- Retenciones (solo lectura de campos Odoo → JSON HKA) ---
        # Detectar retención: manual (dgi_retention_type_id) o automática (posición fiscal)
        retention = getattr(invoice, 'dgi_retention_type_id', None)
        fp = invoice.fiscal_position_id
        is_retention_fp = fp and 'retenci' in (fp.name or '').lower()

        _logger.info(
            "HKA Retención debug: fp=%s, is_retention_fp=%s, sum_itbms=%s, retention=%s",
            fp.name if fp else 'None', is_retention_fp, sum_itbms, retention
        )

        if retention or (is_retention_fp and sum_itbms > 0):
            # Determinar porcentaje de retención
            if retention:
                ret_pct = getattr(retention, 'percentage', 50.0) or 50.0
                ret_code = retention.code or "4"
            elif is_retention_fp:
                # Auto-detectar % de la posición fiscal
                fp_name_lower = (fp.name or '').lower()
                if '100' in fp_name_lower:
                    ret_pct = 100.0
                    ret_code = "1"  # Default gobierno 100%
                else:
                    ret_pct = 50.0
                    ret_code = "4"  # Default contribuyente 50%

            # Usar monto manual si existe; si no, calcular
            manual_amount = getattr(invoice, 'dgi_retention_amount', 0.0)
            if manual_amount:
                ret_amount = round(manual_amount, 2)
            else:
                ret_amount = round(sum_itbms * ret_pct / 100, 2)

            if ret_amount > 0:
                # 'retencion' como OBJETO dentro de totalesSubTotales
                # Ref: https://felwiki.thefactoryhka.com.pa/factura_con_retencion
                # (NO va en datosTransaccion, NO es listaRetenciones array)
                totales_sub_totales["retencion"] = {
                    "codigoRetencion": ret_code,
                    "montoRetencion": f"{ret_amount:.2f}",
                }

        return payload

    def send_document(self, payload):
        """
        Envía el JSON al endpoint de HKA.
        """
        endpoint = f"{self.base_url}/Enviar"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            payload_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            response = requests.post(endpoint, data=payload_bytes, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            # HKA devuelve HTTP 200 incluso si hay error de validación, por lo que revisamos el contenido
            codigo = str(data.get("codigo", ""))
            resultado = str(data.get("resultado", "")).lower()
            
            # Si el código es 200 (éxito en HKA) o el resultado no es error
            is_success = (codigo == "200") or (resultado in ("exito", "exitoso", "ok"))
            
            if not is_success:
                return {
                    "success": False,
                    "error_message": f"Código {codigo}: {data.get('mensaje')}",
                    "raw_response": json.dumps(data, indent=2)
                }
                
            return {
                "success": True,
                "cufe": data.get("cufe") or data.get("cufe_autorizacion"),
                "qr": data.get("qr") or data.get("qrCode"),
                "raw_response": json.dumps(data, indent=2),
            }
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error en comunicación con HKA: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def download_document(self, cufe, tipo_archivo="pdf"):
        """
        Descarga el documento generado por HKA usando el CUFE.
        tipo_archivo puede ser 'pdf' o 'xml'.
        """
        endpoint = f"{self.base_url}/Descarga"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}"
        }
        
        payload = {
            "cufe": cufe,
            "tipoArchivo": tipo_archivo
        }
        
        try:
            payload_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            response = requests.post(endpoint, data=payload_bytes, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            codigo = str(data.get("codigo", data.get("Codigo", "")))
            mensaje = data.get("mensaje", data.get("Mensaje", ""))
            archivo = data.get("archivo", data.get("Archivo", ""))
            
            if (codigo == "200" or codigo == "0") and archivo:
                return {
                    "success": True,
                    "base64": archivo
                }
            else:
                return {
                    "success": False,
                    "error_message": f"Código {codigo}: {mensaje}",
                    "raw_response": json.dumps(data, indent=2)
                }
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error descargando {tipo_archivo} de HKA: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def anular_documento(self, motivo, invoice):
        """
        Envía la solicitud de anulación a HKA.
        """
        endpoint = f"{self.base_url}/Anulacion"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}"
        }
        
        journal_sucursal = invoice.journal_id.l10n_pa_sucursal_code
        company_sucursal = invoice.company_id.l10n_pa_sucursal_code
        codigo_sucursal = (journal_sucursal or company_sucursal or "0000").zfill(4)

        journal_pto = invoice.journal_id.l10n_pa_pto_fact_df
        company_pto = invoice.company_id.l10n_pa_pto_fact
        punto_facturacion = (journal_pto or company_pto or "001").zfill(3)

        payload = {
            "motivoAnulacion": motivo,
            "datosDocumento": {
                "codigoSucursalEmisor": codigo_sucursal,
                "numeroDocumentoFiscal": re.search(r'\d+$', invoice.name).group().zfill(10) if invoice.name and re.search(r'\d+$', invoice.name) else "0000000000",
                "puntoFacturacionFiscal": punto_facturacion,
                "serialDispositivo": "",
                "tipoDocumento": invoice.dgi_document_type_id.code if invoice.dgi_document_type_id else "01",
                "tipoEmision": "01"
            }
        }
        
        try:
            payload_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            response = requests.post(endpoint, data=payload_bytes, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            codigo = str(data.get("codigo", ""))
            resultado = str(data.get("resultado", "")).lower()
            
            is_success = (codigo == "0600") or (resultado in ("exito", "exitoso", "ok", "procesado"))
            
            if not is_success:
                return {
                    "success": False,
                    "error_message": f"Código {codigo}: {data.get('mensaje')}",
                    "raw_response": json.dumps(data, indent=2)
                }
                
            return {
                "success": True,
                "raw_response": json.dumps(data, indent=2),
            }
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error en anulación HKA: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def get_folios_restantes(self):
        """
        Consulta los folios restantes disponibles en HKA.
        Endpoint: GET /api/FoliosRestantes
        """
        endpoint = f"{self.base_url}/FoliosRestantes"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            codigo = str(data.get("codigo", data.get("Codigo", "")))
            resultado = str(data.get("resultado", data.get("Resultado", ""))).lower()

            is_success = (codigo in ("200", "0")) or (resultado in ("exito", "exitoso", "ok"))

            if not is_success:
                return {
                    "success": False,
                    "error_message": f"Código {codigo}: {data.get('mensaje', data.get('Mensaje', 'Error al consultar folios'))}",
                    "raw_response": json.dumps(data, indent=2, ensure_ascii=False)
                }

            return {
                "success": True,
                "licencia": data.get("licencia", data.get("Licencia", "")),
                "fecha_licencia": data.get("fechaLicencia", data.get("FechaLicencia", "")),
                "ciclo": data.get("ciclo", data.get("Ciclo", "")),
                "fecha_ciclo": data.get("fechaCiclo", data.get("FechaCiclo", "")),
                "folios_totales_ciclo": str(data.get("foliosTotalesCiclo", data.get("FoliosTotalesCiclo", "0"))),
                "folios_utilizados_ciclo": str(data.get("foliosUtilizadosCiclo", data.get("FoliosUtilizadosCiclo", "0"))),
                "folios_disponibles_ciclo": str(data.get("foliosDisponibleCiclo", data.get("FoliosDisponibleCiclo", "0"))),
                "folios_totales": str(data.get("foliosTotales", data.get("FoliosTotales", "0"))),
                "folios_totales_disponibles": str(data.get("foliosTotalesDisponibles", data.get("FoliosTotalesDisponibles", "0"))),
                "mensaje": data.get("mensaje", data.get("Mensaje", "")),
                "raw_response": json.dumps(data, indent=2, ensure_ascii=False)
            }
        except requests.exceptions.RequestException as e:
            _logger.error("Error consultando folios HKA: %s", e)
            return {
                "success": False,
                "error_message": str(e)
            }

