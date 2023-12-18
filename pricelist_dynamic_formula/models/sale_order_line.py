from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_pricelist_price(self):
        price = super(SaleOrderLine, self)._get_pricelist_price()
        if self.pricelist_item_id.compute_price == 'dynamic_formula' and self.pricelist_item_id.python_code:
            price = self.pricelist_item_id.compute_dynamic_price(order_id=self.order_id,
                                                                 partner_id=self.order_id.partner_id,
                                                                 product_id=self.product_id.id)
        return price
