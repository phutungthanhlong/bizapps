# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    sh_dynamic_product_fields_ids = fields.Many2many(string="Product Fields",
                                                     comodel_name="ir.model.fields",
                                                     )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sh_dynamic_product_fields_ids = fields.Many2many(string="Product Fields",
                                                     comodel_name="ir.model.fields",
                                                     related="website_id.sh_dynamic_product_fields_ids",
                                                     domain=[('model_id.model', 'in', ['product.template']),
                                                             ('ttype', 'in', [
                                                              'char', 'date', 'datetime', 'float', 'boolean', 'integer', 'text', 'html', 'many2one', 'selection', 'binary']),
                                                             ('store', '=', True)
                                                             ],
                                                     readonly=False,
                                                     )
