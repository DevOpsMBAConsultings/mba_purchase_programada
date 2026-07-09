# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError
import requests
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_validate_dgi(self):
        """ Override of base action to get RUC details from HKA """
        self.ensure_one()
        
        # Mapear Términos de pago (Ventas y compras) → campos DGI si no se han rellenado
        payment_term = getattr(self.with_company(self.env.company), "property_payment_term_id", None)
        if payment_term:
            dgi_vals = self._dgi_payment_vals_from_payment_term(payment_term)
            if dgi_vals:
                self.with_context(skip_fe_validation=True).write({
                    "dgi_payment_term_type": dgi_vals.get("dgi_payment_term_type"),
                    "dgi_payment_method_id": dgi_vals.get("dgi_payment_method_id"),
                    "dgi_plazo_option": dgi_vals.get("dgi_plazo_option", "30"),
                })

        if not self.id:
            return self._dgi_notification_error(
                "Validación incompleta",
                "Guarde primero el contacto."
            )

        vat_value = self.vat or ""
        ruc = vat_value.strip()

        # Validaciones de campos obligatorios para DGI
        if not self.l10n_pa_receptor_tipo:
            return self._dgi_notification_error(
                "Validación incompleta",
                "Debe seleccionar el Tipo de Receptor (DGI) antes de validar."
            )
            
        if self.l10n_pa_receptor_tipo == '02' and self.company_type == 'company':
            return self._dgi_notification_error(
                "Validación de Tipo de Receptor",
                "No puedes declarar a una empresa (Persona Jurídica) como Consumidor Final."
            )

        if not ruc and self.l10n_pa_receptor_tipo != '02':
            return self._dgi_notification_error(
                "Validación incompleta", 
                "Por favor ingrese el RUC o Cédula en el campo correspondiente antes de validar."
            )
            
        if self.l10n_pa_receptor_tipo in ("01", "03"):
            if not self.l10n_pa_provincia_id or not self.l10n_pa_distrito_id or not self.l10n_pa_corregimiento_id:
                return self._dgi_notification_error(
                    "Validación incompleta",
                    "Provincia, Distrito y Corregimiento son obligatorios para Contribuyente y Gobierno (DGI)."
                )
            if not (self.street or self.street2 or self.city):
                return self._dgi_notification_error(
                    "Validación incompleta",
                    "Favor introducir una dirección en el contacto (Calle / Ciudad). Es requerida para facturar a Contribuyente/Gobierno."
                )
                
        self.invalidate_recordset()
        if not getattr(self, "dgi_payment_method_id", False):
            return self._dgi_notification_error(
                "Validación incompleta",
                "Debe seleccionar un Método de Pago (DGI) o Término de Pago antes de validar."
            )

        # Bypass API validation for Consumidor Final (02) if no RUC provided or it's "CF"
        if self.l10n_pa_receptor_tipo == '02' and (not ruc or ruc.upper() == 'CF'):
            vals = {
                "l10n_pa_is_dgi_validated": True,
            }
            if not ruc:
                vals["vat"] = "CF"
                
            # Limpiar / Formatear los campos estándar para FE (como en facturacion_electronica_18)
            raw_phone = (self.phone or "").strip()
            if self.country_id and self.country_id.code == "PA":
                formatted_phone = self._format_panama_phone(raw_phone, self.country_id) or False
            else:
                formatted_phone = self._format_dgi_phone_any_country(raw_phone) or False
                
            if formatted_phone:
                vals["phone"] = formatted_phone
                
            if self.street:
                vals["street"] = self.street[:100] # Address max length is 100
                
            self.with_context(skip_fe_validation=True).write(vals)
            self.message_post(
                body="✅ <b>Validación DGI completada</b><br/>Tipo: Consumidor Final (sin RUC)",
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Datos DGI validados",
                    "message": "Consumidor Final validado correctamente (sin RUC).",
                    "type": "success",
                    "sticky": True,
                },
            }

        company = self.env.company
        if not company.l10n_pa_hka_user or not company.l10n_pa_hka_password:
            return self._dgi_notification_error(
                "Configuración faltante",
                "Por favor configure las credenciales de HKA (Usuario y Contraseña) en los Ajustes de la Compañía."
            )

        try:
            company.sudo().action_hka_get_token()
            
            url = f"{company.l10n_pa_hka_url}/ConsultaRucDv"
            headers = {
                'Authorization': f'Bearer {company.l10n_pa_hka_token}',
                'Content-Type': 'application/json'
            }
            
            last_error_msg = ""
            success_data = None
            
            # DGI/HKA: tipoRuc "1" = Persona Natural, "2" = Persona Jurídica
            # Buscar primero el tipo que corresponde al tipo de contacto en Odoo
            if self.company_type == 'company':
                tipos_to_try = ("2", "1")  # Jurídica primero
            else:
                tipos_to_try = ("1", "2")  # Natural primero
            for tipo in tipos_to_try:
                payload = {"ruc": ruc, "tipoRuc": tipo}
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=20)
                    if response.status_code == 200:
                        data = response.json()
                        if str(data.get("codigo")) == "200" and data.get("infoRuc"):
                            success_data = data["infoRuc"]
                            if not success_data.get("tipoRuc"):
                                success_data["tipoRuc"] = tipo
                            break
                        else:
                            last_error_msg = data.get("mensaje", "RUC no encontrado por HKA.")
                    else:
                        last_error_msg = f"Error HTTP {response.status_code}"
                except requests.exceptions.RequestException as e:
                    last_error_msg = str(e)
            
            if not success_data:
                return self._dgi_notification_error(
                    "Error de validación", 
                    f"No se pudo obtener la información de la DGI. HKA respondió: {last_error_msg}"
                )
                
            dv = success_data.get("dv")
            razon_social = success_data.get("razonSocial")
            tipo_ruc = str(success_data.get("tipoRuc") or "").strip()
            
            vals = {}
            if razon_social:
                vals["l10n_pa_razon_social"] = razon_social

            if dv is not None and str(dv).strip():
                digits = re.sub(r"\D", "", str(dv).strip())
                vals["l10n_pa_dv"] = digits.zfill(2)[-2:] if digits else False
            else:
                vals["l10n_pa_dv"] = False
                
            # Mapeo DIRECTO: DGI tipoRuc "1"=Natural → tipoContribuyente "1", "2"=Jurídica → "2"
            if tipo_ruc in ("1", "2"):
                vals["l10n_pa_tipo_contribuyente"] = tipo_ruc
            else:
                vals["l10n_pa_tipo_contribuyente"] = False
            
            # Limpiar / Formatear los campos estándar para FE (como en facturacion_electronica_18)
            raw_phone = (self.phone or "").strip()
            if self.country_id and self.country_id.code == "PA":
                formatted_phone = self._format_panama_phone(raw_phone, self.country_id) or False
            else:
                formatted_phone = self._format_dgi_phone_any_country(raw_phone) or False
                
            if formatted_phone:
                vals["phone"] = formatted_phone
                
            if self.street:
                vals["street"] = self.street[:100] # Address max length is 100
                
            vals["l10n_pa_is_dgi_validated"] = True
            self.with_context(skip_fe_validation=True).write(vals)
            self.message_post(
                body=(
                    f"✅ <b>Validación DGI completada</b><br/>"
                    f"Razón Social: {razon_social or 'N/A'}<br/>"
                    f"DV: {vals.get('l10n_pa_dv', 'N/A')}<br/>"
                    f"Tipo Contribuyente: {'Natural' if tipo_ruc == '1' else 'Jurídica' if tipo_ruc == '2' else 'N/A'}"
                ),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Datos DGI validados",
                    "message": f"Datos validados y formateados correctamente. Razón Social: {razon_social or 'No devuelta'}",
                    "type": "success",
                    "sticky": True,
                },
            }
            
        except requests.exceptions.RequestException as e:
            return self._dgi_notification_error(
                "Error de conexión",
                f"No se pudo conectar con el API de HKA: {str(e)}"
            )
