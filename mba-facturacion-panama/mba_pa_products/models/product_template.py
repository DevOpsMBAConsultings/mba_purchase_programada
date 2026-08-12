# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    dgi_unidad_medida_id = fields.Many2one(
        "dgi.unidad.medida",
        string="Unidad de medida (DGI)",
        ondelete="restrict",
    )

    dgi_cpbs_segment_id = fields.Many2one(
        "dgi.cpbs.segment",
        string="Clasificación bienes/servicios (DGI)",
        ondelete="restrict",
    )

    dgi_cpbs_family_id = fields.Many2one(
        "dgi.cpbs.family",
        string="Subclasificación bienes/servicios (DGI)",
        ondelete="restrict",
        domain="[('segment_id', '=', dgi_cpbs_segment_id)]",
    )

    dgi_cpbs_abrev = fields.Char(
        string="Código CPBMS abreviado",
        help="Código abreviado CPBMS (según catálogo DGI).",
    )

    dgi_cpbs_codigo = fields.Char(
        string="Código codificación panameña del ítem",
        help="Código oficial de la codificación panameña (según catálogo DGI).",
    )

    dgi_charge_type = fields.Selection(
        [
            ("", "Ninguno (ítem normal)"),
            ("acarreo", "Acarreo (FACTURA)"),
            ("seguro", "Seguro (SEGURO)"),
            ("otros_gastos", "Otros Gastos (OTROS_GASTOS)"),
        ],
        string="Cargo DGI (F03)",
        default="",
        help="Si se selecciona, las líneas con este producto no se envían como ítem normal; "
        "se agregan a TotalCharges (F03) con la descripción indicada.",
    )

    @api.onchange("dgi_cpbs_segment_id")
    def _onchange_dgi_cpbs_segment_id(self):
        for rec in self:
            if rec.dgi_cpbs_family_id and rec.dgi_cpbs_family_id.segment_id != rec.dgi_cpbs_segment_id:
                rec.dgi_cpbs_family_id = False

    @api.constrains("dgi_cpbs_segment_id", "dgi_cpbs_family_id")
    def _check_segment_family_consistency(self):
        for rec in self:
            if rec.dgi_cpbs_family_id and rec.dgi_cpbs_segment_id:
                if rec.dgi_cpbs_family_id.segment_id != rec.dgi_cpbs_segment_id:
                    raise ValidationError(_("La Familia (DGI) no pertenece al Segmento seleccionado."))

    @api.constrains("dgi_cpbs_abrev", "dgi_cpbs_codigo")
    def _check_dgi_codes_length(self):
        for rec in self:
            if rec.dgi_cpbs_abrev and len(rec.dgi_cpbs_abrev.strip()) > 50:
                raise ValidationError(_("El Código CPBMS abreviado excede 50 caracteres."))
            if rec.dgi_cpbs_codigo and len(rec.dgi_cpbs_codigo.strip()) > 50:
                raise ValidationError(_("El Código de codificación panameña excede 50 caracteres."))

    @api.constrains("taxes_id", "sale_ok", "dgi_charge_type")
    def _check_taxes_assigned(self):
        """
        Validación: Todos los productos vendibles deben tener al menos un impuesto positivo asignado
        para la Facturación Electrónica en Panamá.
        """
        # Omitir validación durante instalación/actualización automática de módulos
        if self.env.context.get('install_mode'):
            return

        for rec in self:
            if rec.sale_ok:
                if rec.dgi_charge_type in ["acarreo", "seguro", "otros_gastos"]:
                    continue

                def is_retention(tax):
                    if getattr(tax, 'dgi_is_retention', False):
                        return True
                    if tax.amount < 0:
                        return True
                    name = (tax.name or "").lower()
                    group_name = (tax.tax_group_id.name or "").lower() if tax.tax_group_id else ""
                    return "retenc" in name or "retenc" in group_name or "reten" in name or "reten" in group_name
                    
                if not rec.taxes_id or all(is_retention(tax) for tax in rec.taxes_id):
                    # Solo es una advertencia o log en implementaciones limpias,
                    # para no romper otras dependencias de odoo, pero como estaba en constrains, lo mantenemos:
                    raise ValidationError(
                        _("No se puede guardar el producto '%s': debe tener al menos un impuesto positivo "
                          "(ITBMS, incluyendo 0%%) asignado en los 'Impuestos de venta'.\n\n"
                          "La DGI exige que todos los productos facturables declaren un impuesto base. "
                          "Las retenciones por sí solas no son suficientes.") % rec.name
                    )

    def write(self, vals):
        res = super().write(vals)
        if "standard_price" in vals:
            action = self._update_sale_price_from_base_pricelist(show_notification=True)
            if action:
                return action
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any("standard_price" in vals for vals in vals_list):
            records._update_sale_price_from_base_pricelist(show_notification=True)
        return records

    def _update_sale_price_from_base_pricelist(self, show_notification=False):
        """
        Recalcula el precio de venta (list_price) para los productos cuando cambia el costo (standard_price)
        usando la lista de precios base configurada en la compañía.
        """
        company = self.env.company
        pricelist = company.base_pricelist_compute_price_id
        if not pricelist:
            return

        updated_templates = []
        for tmpl in self:
            pricelist_data = pricelist._compute_price_rule(tmpl, 1)
            new_price, suitable_rule = pricelist_data.get(tmpl.id, (False, False))
            if suitable_rule and new_price is not False and new_price != tmpl.list_price:
                tmpl.write({"list_price": new_price})
                updated_templates.append((tmpl.name, new_price))

        if show_notification and updated_templates and len(self) == 1 and not self.env.context.get("import_file"):
            name, price = updated_templates[0]
            currency_symbol = company.currency_id.symbol or "B/."
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Precio de Venta Actualizado"),
                    "message": _("El precio de venta para '%s' fue actualizado a %s %.2f según la Lista de Precios.") % (name, currency_symbol, price),
                    "type": "success",
                    "sticky": False,
                },
            }


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super().write(vals)
        if "standard_price" in vals:
            templates = self.mapped("product_tmpl_id")
            action = templates._update_sale_price_from_base_pricelist(show_notification=True)
            if action:
                return action
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any("standard_price" in vals for vals in vals_list):
            templates = records.mapped("product_tmpl_id")
            templates._update_sale_price_from_base_pricelist(show_notification=True)
        return records


