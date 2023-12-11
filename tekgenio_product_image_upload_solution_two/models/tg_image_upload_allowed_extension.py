from odoo import fields, models


class TgImageUploadLogAllowedExtension(models.Model):
    _name = "tg.image.upload.allowed.extension"

    name = fields.Char(string = "Image Extension")
    # res_config_id = fields.Many2one("res.config.settings", "Res Config")
