# -*- coding: utf-8 -*-
from odoo import models, fields


class PriceListGrade(models.Model):
    _name = 'grade.product.pricelist'

    name = fields.Char(string="Name")
    partner_ids = fields.One2many('res.partner', 'grade_id', string="Partner")
    pricelist_ids = fields.One2many("product.pricelist", 'grade_id', string="Price List")