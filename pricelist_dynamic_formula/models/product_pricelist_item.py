from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
import json


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    compute_price = fields.Selection(selection_add=[
        ('dynamic_formula', 'Dynamic Formula'),
    ], ondelete={'dynamic_formula': 'cascade'})
    python_code = fields.Text(string='Formula', default='''
# Available variables:
#----------------------
# Product: product.product object
# Note: returned value have to be set in the variable 'result'
        
result = 0''')

    def _raise_error(self, local_dict, error_type, e):
        raise UserError(_("""%s:
            - Order: %s
            - Partner: %s
            - Product: %s
            - Item: %s
            - Error: %s""") % (
            error_type,
            local_dict['order'].name,
            local_dict['partner'].name,
            local_dict['product'].dict.name,
            self.id,
            e))

    def _satisfy_condition(self, local_dict):
        self.ensure_one()
        try:
            safe_eval(self.python_code, local_dict, mode='exec', nocopy=True)
            return float(local_dict.get('result', 0))
        except Exception as e:
            self._raise_error(local_dict, _("Wrong python condition defined for:"), e)

    def compute_dynamic_price(self, order_id=False, partner_id=False, product_id=False):
        local_dict = {
            'order': order_id,
            'partner': partner_id,
            'product': self.env['product.product'].browse(product_id),
            'result': 0,
        }
        price = self._satisfy_condition(local_dict)
        return price
