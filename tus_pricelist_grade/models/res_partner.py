from odoo import api, models, fields

class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    grade_id = fields.Many2one('grade.product.pricelist', string="Grade")
    property_product_pricelist = fields.Many2one('product.pricelist', string="Pricelist")

    @api.onchange('grade_id')
    def onchange_grade_id(self):
        """
        Update property_product_pricelist based on grade_id.
        """
        if self.grade_id:
            # Tìm danh sách giá dựa trên grade_id
            pricelist_ids = self.grade_id.pricelist_ids
            if pricelist_ids:
                # Lấy giá trị của pricelist từ danh sách giá
                new_pricelist_id = pricelist_ids[0].id
                self.property_product_pricelist = new_pricelist_id
        else:
            # Nếu grade_id bị xóa, bạn có thể đặt property_product_pricelist về giá trị mặc định hoặc giá trị rỗng tùy vào yêu cầu của bạn.
            self.property_product_pricelist = False
