from odoo import api, models, fields

class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    grade_id = fields.Many2one('grade.product.pricelist', string="Grade")
    property_product_pricelist = fields.Many2one('product.pricelist', string="Pricelist", compute='_compute_property_product_pricelist', store=True)

    @api.depends('grade_id')
    def _compute_property_product_pricelist(self):
        for partner in self:
            if partner.grade_id:
                new_pricelist_id = self._get_new_pricelist_id(partner.grade_id)
                partner.property_product_pricelist = new_pricelist_id
            else:
                partner.property_product_pricelist = False

    def _get_new_pricelist_id(self, grade):
        # Lấy giá trị đầu tiên tương ứng với grade_id
        new_pricelist_id = grade.pricelist_ids and grade.pricelist_ids[0].id
        return new_pricelist_id
