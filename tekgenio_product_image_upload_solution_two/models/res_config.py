from odoo import models, fields, api
from ast import literal_eval


class TekgGenioResConfig(models.TransientModel):
    _inherit = "res.config.settings"
    _description = "Res Config Settings"

    allowed_image_extension_ids = fields.Many2many("tg.image.upload.allowed.extension", string="Allowed Extensions")

    def set_values(self):
        res = super(TekgGenioResConfig, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'tekgenio_product_image_upload_solution_two.allowed_image_extension_ids',
            self.allowed_image_extension_ids.ids)
        print(self.allowed_image_extension_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(TekgGenioResConfig, self).get_values()
        config_values = self.env['ir.config_parameter'].sudo()
        allowed_values = config_values.get_param(
            'tekgenio_product_image_upload_solution_two.allowed_image_extension_ids')
        if allowed_values:
            res.update(
                allowed_image_extension_ids=[(6, 0, literal_eval(allowed_values))],
            )
        return res
