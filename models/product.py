from odoo import models, fields, api
from lxml import etree


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == 'list':
            arch_el = etree.fromstring(res['arch'])
            target = arch_el.xpath("//field[@name='list_price']") or arch_el.xpath("//field[@name='lst_price']") or arch_el.xpath("//field[@name='name']")
            if target:
                pricelists = self.env["product.pricelist"].search(
                    [("display_in_product_list", "=", True)],
                    order="sequence, id"
                )
                if 'models' in res:
                    res['models'] = dict(res['models'])
                current_target = target[0]
                for pricelist in pricelists:
                    field_name = f"price_pricelist_{pricelist.id}"
                    if not arch_el.xpath(f"//field[@name='{field_name}']"):
                        new_field = etree.Element('field', name=field_name, optional="show")
                        current_target.addnext(new_field)
                        current_target = new_field
                        
                        # Add field name to the view models tuple
                        if 'models' in res and self._name in res['models']:
                            fields_list = list(res['models'][self._name])
                            if field_name not in fields_list:
                                res['models'][self._name] = tuple(fields_list + [field_name])
                res['arch'] = etree.tostring(arch_el, encoding='unicode')
        return res

    @api.model
    def fields_get(self, allfields=None, **kwargs):
        res = super().fields_get(allfields, **kwargs)
        pricelists = self.env["product.pricelist"].search(
            [("display_in_product_list", "=", True)],
            order="sequence, id"
        )
        for pricelist in pricelists:
            field_name = f"price_pricelist_{pricelist.id}"
            res[field_name] = {
                'type': 'float',
                'string': f"Price ({pricelist.name})",
                'readonly': True,
                'sortable': False,
                'searchable': False,
                'store': False,
            }
        return res

    def read(self, fields=None, load='_classic_read'):
        if fields:
            pricelist_fields = [f for f in fields if f.startswith('price_pricelist_')]
            standard_fields = [f for f in fields if not f.startswith('price_pricelist_')]
            
            res = super().read(standard_fields, load=load)
            
            if pricelist_fields:
                pricelist_ids = [int(f.replace('price_pricelist_', '')) for f in pricelist_fields]
                pricelists = self.env['product.pricelist'].browse(pricelist_ids)
                pricelist_map = {p.id: p for p in pricelists}
                
                for record_dict in res:
                    record = self.browse(record_dict['id'])
                    product = record.product_variant_id
                    for f in pricelist_fields:
                        p_id = int(f.replace('price_pricelist_', ''))
                        pricelist = pricelist_map.get(p_id)
                        if pricelist and product:
                            try:
                                record_dict[f] = pricelist._get_product_price(product, quantity=1.0)
                            except Exception:
                                record_dict[f] = 0.0
                        else:
                            record_dict[f] = 0.0
            return res
        return super().read(fields, load=load)

    @api.model
    def web_search_read(self, domain=None, specification=None, offset=0, limit=None, order=None, count_limit=None):
        if specification:
            pricelist_fields = {f: v for f, v in specification.items() if f.startswith('price_pricelist_')}
            standard_specification = {f: v for f, v in specification.items() if not f.startswith('price_pricelist_')}
            
            res = super().web_search_read(domain=domain, specification=standard_specification, offset=offset, limit=limit, order=order, count_limit=count_limit)
            
            if pricelist_fields and 'records' in res:
                pricelist_ids = [int(f.replace('price_pricelist_', '')) for f in pricelist_fields]
                pricelists = self.env['product.pricelist'].browse(pricelist_ids)
                pricelist_map = {p.id: p for p in pricelists}
                
                for record_dict in res['records']:
                    record = self.browse(record_dict['id'])
                    product = record.product_variant_id
                    for f in pricelist_fields:
                        p_id = int(f.replace('price_pricelist_', ''))
                        pricelist = pricelist_map.get(p_id)
                        if pricelist and product:
                            try:
                                record_dict[f] = pricelist._get_product_price(product, quantity=1.0)
                            except Exception:
                                record_dict[f] = 0.0
                        else:
                            record_dict[f] = 0.0
            return res
        return super().web_search_read(domain=domain, specification=specification, offset=offset, limit=limit, order=order, count_limit=count_limit)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == 'list':
            arch_el = etree.fromstring(res['arch'])
            target = arch_el.xpath("//field[@name='list_price']") or arch_el.xpath("//field[@name='lst_price']") or arch_el.xpath("//field[@name='name']")
            if target:
                pricelists = self.env["product.pricelist"].search(
                    [("display_in_product_list", "=", True)],
                    order="sequence, id"
                )
                if 'models' in res:
                    res['models'] = dict(res['models'])
                current_target = target[0]
                for pricelist in pricelists:
                    field_name = f"price_pricelist_{pricelist.id}"
                    if not arch_el.xpath(f"//field[@name='{field_name}']"):
                        new_field = etree.Element('field', name=field_name, optional="show")
                        current_target.addnext(new_field)
                        current_target = new_field
                        
                        # Add field name to the view models tuple
                        if 'models' in res and self._name in res['models']:
                            fields_list = list(res['models'][self._name])
                            if field_name not in fields_list:
                                res['models'][self._name] = tuple(fields_list + [field_name])
                res['arch'] = etree.tostring(arch_el, encoding='unicode')
        return res

    @api.model
    def fields_get(self, allfields=None, **kwargs):
        res = super().fields_get(allfields, **kwargs)
        pricelists = self.env["product.pricelist"].search(
            [("display_in_product_list", "=", True)],
            order="sequence, id"
        )
        for pricelist in pricelists:
            field_name = f"price_pricelist_{pricelist.id}"
            res[field_name] = {
                'type': 'float',
                'string': f"Price ({pricelist.name})",
                'readonly': True,
                'sortable': False,
                'searchable': False,
                'store': False,
            }
        return res

    def read(self, fields=None, load='_classic_read'):
        if fields:
            pricelist_fields = [f for f in fields if f.startswith('price_pricelist_')]
            standard_fields = [f for f in fields if not f.startswith('price_pricelist_')]
            
            res = super().read(standard_fields, load=load)
            
            if pricelist_fields:
                pricelist_ids = [int(f.replace('price_pricelist_', '')) for f in pricelist_fields]
                pricelists = self.env['product.pricelist'].browse(pricelist_ids)
                pricelist_map = {p.id: p for p in pricelists}
                
                for record_dict in res:
                    product = self.browse(record_dict['id'])
                    for f in pricelist_fields:
                        p_id = int(f.replace('price_pricelist_', ''))
                        pricelist = pricelist_map.get(p_id)
                        if pricelist and product:
                            try:
                                record_dict[f] = pricelist._get_product_price(product, quantity=1.0)
                            except Exception:
                                record_dict[f] = 0.0
                        else:
                            record_dict[f] = 0.0
            return res
        return super().read(fields, load=load)

    @api.model
    def web_search_read(self, domain=None, specification=None, offset=0, limit=None, order=None, count_limit=None):
        if specification:
            pricelist_fields = {f: v for f, v in specification.items() if f.startswith('price_pricelist_')}
            standard_specification = {f: v for f, v in specification.items() if not f.startswith('price_pricelist_')}
            
            res = super().web_search_read(domain=domain, specification=standard_specification, offset=offset, limit=limit, order=order, count_limit=count_limit)
            
            if pricelist_fields and 'records' in res:
                pricelist_ids = [int(f.replace('price_pricelist_', '')) for f in pricelist_fields]
                pricelists = self.env['product.pricelist'].browse(pricelist_ids)
                pricelist_map = {p.id: p for p in pricelists}
                
                for record_dict in res['records']:
                    product = self.browse(record_dict['id'])
                    for f in pricelist_fields:
                        p_id = int(f.replace('price_pricelist_', ''))
                        pricelist = pricelist_map.get(p_id)
                        if pricelist and product:
                            try:
                                record_dict[f] = pricelist._get_product_price(product, quantity=1.0)
                            except Exception:
                                record_dict[f] = 0.0
                        else:
                            record_dict[f] = 0.0
            return res
        return super().web_search_read(domain=domain, specification=specification, offset=offset, limit=limit, order=order, count_limit=count_limit)
