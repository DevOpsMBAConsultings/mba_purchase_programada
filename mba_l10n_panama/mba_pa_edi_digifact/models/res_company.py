# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    df_fe_environment = fields.Selection([
        ('test', 'Pruebas'),
        ('prod', 'Producción'),
    ], string='Ambiente (Digifact)', default='test', required=True)
    df_fe_username = fields.Char(string='Usuario (Digifact)')
    df_fe_password = fields.Char(string='Contraseña (Digifact)')

    def action_get_ruc_details(self):
        """ Override of base action to get RUC details from Digifact """
        self.ensure_one()
        # Ensure credentials
        if not self.df_fe_username or not self.df_fe_password:
            raise UserError("Por favor configure las credenciales de Digifact (Usuario y Contraseña) en la pestaña FE (DGI-ADMIN).")

        vat_value = self.vat or ""
        if not vat_value:
            raise UserError("Por favor ingrese el RUC en el campo NIF/VAT antes de obtener los detalles.")

        ruc = vat_value.strip()

        try:
            self.action_digifact_get_token()
            client = self.env["digifact.client"]
            
            data = None
            for tipo in [2, 1]:
                try:
                    status, payload = client.get_info_ruc(ruc=ruc, tipo=tipo, company=self)
                    if payload and payload.get("Ok") is True:
                        data = payload
                        break
                except Exception:
                    continue
            
            if not data:
                raise UserError(f"El RUC {ruc} no fue encontrado o es inválido en Digifact.")
            
            dv = data.get("DV") or data.get("Dv") or data.get("dv") or data.get("DigitoVerificador")
            razon_social = data.get("RazonSocial") or data.get("Razon_Social") or data.get("RazonSocialFE") or data.get("Nombre") or data.get("name")
            tipo_ruc = str(data.get("TipoRuc") or data.get("TipoRUC") or data.get("TipoEmpresa") or "").strip()
            
            # Save the related values directly to the partner
            vals = {}
            if dv and str(dv).strip():
                import re
                digits = re.sub(r"\D", "", str(dv).strip())
                vals["l10n_pa_dv"] = digits.zfill(2)[-2:] if digits else False
            else:
                vals["l10n_pa_dv"] = False
            
            if tipo_ruc in ("1", "2"):
                vals["l10n_pa_tipo_contribuyente"] = tipo_ruc
            
            self.partner_id.write(vals)

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Éxito",
                    "message": f"Los detalles del RUC {ruc} se obtuvieron correctamente desde Digifact.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except UserError:
            raise
        except Exception as e:
            raise UserError(f"Error al obtener los detalles del RUC: {str(e)}")

    def action_digifact_get_token(self):
        self.ensure_one()
        if not self.df_fe_username or not self.df_fe_password:
            raise UserError("Por favor configure las credenciales de Digifact (Usuario y Contraseña).")
        
        try:
            client = self.env["digifact.client"]
            token_data = client.get_token(username=self.df_fe_username, password=self.df_fe_password, company=self)
            
            if not token_data:
                raise UserError("No se pudo obtener el token de Digifact. Verifique las credenciales.")
            
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Éxito",
                    "message": "Token de Digifact obtenido correctamente.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            raise UserError(f"Error al obtener el token: {str(e)}")

    def action_digifact_test_connection(self):
        self.ensure_one()
        self.action_digifact_get_token()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Conexión Exitosa",
                "message": "La conexión con Digifact se estableció correctamente.",
                "type": "success",
                "sticky": False,
            },
        }
