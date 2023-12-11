# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import _


class WebsiteSaleCustom(WebsiteSale):

    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        """
            INHERIT CONTROLLER BY SOFTHEALER TECHNOLOGIES
            to get product value to detail page website
        """
        res = super(WebsiteSaleCustom, self).product(
            product, category, search, **kwargs)
        if request.website and request.website.sudo().sh_dynamic_product_fields_ids:
            post_msg = ""
            for product_field in request.website.sudo().sh_dynamic_product_fields_ids:
                field_value = ""

                if product_field.ttype in ['char', 'date', 'datetime', 'float', 'boolean', 'integer', 'text', 'html']:
                    field_value = getattr(product, '%s' % (product_field.name))

                elif product_field.ttype in ['many2one']:
                    field_value = getattr(product, '%s' % (product_field.name))
                    if field_value:
                        field_value = field_value.sudo().name
                        if not field_value:
                            field_value = ""

                elif product_field.ttype in ['selection']:
                    field_value = getattr(product, '%s' % (product_field.name))
                    selection_key_value_list = request.env['product.template'].sudo(
                    )._fields[product_field.name].selection
                    selection_dic = {}

                    if selection_key_value_list:
                        selection_dic = dict(selection_key_value_list)

                    if selection_dic:
                        field_value = selection_dic.get(field_value, "")

                elif product_field.ttype in ['binary']:
                    field_value = _('''
                    <a href="/web/content/product.template/%(product_id)s/%(field_name)s?download=true">%(field_description)s</a>
                    ''') % {
                        'field_name': product_field.name,
                        'product_id': product.id,
                        'field_description': product_field.field_description
                    }

                # finally make empty string if there is no field value or has false field value
                if not field_value:
                    field_value = ""
                barcode = request.env['product.template'].add_barcode_value()
                if field_value:
                    post_msg += _('''
                    <span>
                        <strong> %(field_description)s: </strong> %(field_value)s 
                    </span><br/>
            ''') % {
                        'field_description': product_field.field_description,
                        'field_value': field_value,
                        'barcode':barcode
                    }

                print("\n\n\n\n\n....post_msg......",post_msg)
            product.sudo().sh_dynamic_product_fields_raw_html = post_msg

        return res
