# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    grade_id = fields.Many2one('grade.product.pricelist', string="Grade")

    @api.onchange('grade_id')
    def onchange_grade_id(self):
        """
        remove the price list value each time the Grade is selected
        """
        self.property_product_pricelist = False
        self.property_product_pricelist = True