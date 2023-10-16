# -*- coding: utf-8 -*-
from odoo import models, fields


class PricelistExt(models.Model):
    _inherit = "product.pricelist"

    grade_id = fields.Many2one('grade.product.pricelist', string="Grade")
