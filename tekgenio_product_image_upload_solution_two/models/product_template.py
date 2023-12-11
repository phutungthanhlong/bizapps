from odoo import fields, models, _


class TekgenioProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_call_clean_wizard(self):
        if self:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'target': 'new',
                'name': _('Clean Extra Images'),
                'res_model': 'clean.extra.images.wizard',
                'context': {'default_product_tmpl_ids': self.ids}
            }
