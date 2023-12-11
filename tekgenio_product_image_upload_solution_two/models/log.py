from odoo import fields, models


class ProductImageUploadLog(models.Model):
    _name = "product.image.upload.log"
    _order = 'id desc'

    name = fields.Char(string="Name",
                       default=lambda self: self.env['ir.sequence'].next_by_code('product.image.upload.log'),
                       readonly=True)
    import_timestamp = fields.Datetime(readonly=True, string="Time")
    salesperson_id = fields.Many2one('res.users', string="User", readonly=True)
    root_path = fields.Char(string="Upload Root Path", readonly=True)
    status = fields.Char(string="Status", readonly=True)
    product_image_upload_line_ids = fields.One2many('product.image.upload.log.line', 'log_id',
                                                    string="Product Image Upload Log Lines", readonly=True)


class ProductImageUploadLogLine(models.Model):
    _name = "product.image.upload.log.line"
    _order = 'barcode desc'

    barcode = fields.Char(string="Barcode", readonly=True)
    log_status = fields.Char(string="Import Status",readonly=True)
    log_message = fields.Char(string="Import Message", readonly=True)
    log_type = fields.Char(string="Log Type", readonly=True)
    log_id = fields.Many2one("product.image.upload.log", string="Product Image Upload Log", readonly=True)
