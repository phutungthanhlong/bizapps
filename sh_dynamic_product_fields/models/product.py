# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sh_dynamic_product_fields_raw_html = fields.Html(
        'Product Fields Data', translate=True)
    
    def add_barcode_value(self):
        print("\n\n\n\n...SELF......",self)
        
        return self.barcode