# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

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
            pricelist_data = pricelist.with_company(company)._compute_price_rule(tmpl, 1)
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

    def _set_standard_price(self):
        super()._set_standard_price()
        templates = self.mapped("product_tmpl_id")
        templates._update_sale_price_from_base_pricelist(show_notification=True)
