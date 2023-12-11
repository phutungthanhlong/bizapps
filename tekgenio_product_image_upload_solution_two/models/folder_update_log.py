from odoo import fields, models


class FolderUpdateLog(models.Model):
    _name = 'folder.update.log'
    _description = 'Folder Update Log'
    _order = 'root_modified_date desc'

    root_path = fields.Char(string='Root Path')
    root_modified_date = fields.Datetime(string='Root Modified Date')
    folder_path = fields.Char(string='Folder Path')
    modified_date = fields.Datetime(string='Modified Date')
    count = fields.Char(string="Number Of Files")
