from odoo import api,SUPERUSER_ID
from . import models
from . import controllers
from . import wizard

def uninstall_hook(cr, registry):
    print("uninstall hooks")
    env = api.Environment(cr, SUPERUSER_ID, {})
    ICP = env['ir.config_parameter']
    ICP.set_param('tekgenio_product_image_upload_solution_two.allowed_image_extension_ids', '')


