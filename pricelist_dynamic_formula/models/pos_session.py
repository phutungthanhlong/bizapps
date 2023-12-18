from odoo import models, fields, api, _
import json


class PosSession(models.Model):
    _inherit = 'pos.session'

    def load_pos_data(self):
        res = super(PosSession, self).load_pos_data()
        if res:
            for pricelist in res.get('product.pricelist', []):
                items = pricelist.get('items', [])
                for x in range(0, len(items)):
                    if items[x].get('compute_price', '') == 'dynamic_formula':
                        pricelist_item = self.env['product.pricelist.item'].browse(items[x]['id'])
                        list_product_price = {}
                        for product in res.get('product.product', []):
                            price = pricelist_item.compute_dynamic_price(product_id=product['id'])
                            list_product_price.update({product['id']: price})
                        items[x].update({'list_product_price': json.dumps(list_product_price)})
                        pricelist.get('items', [])[x] = items[x]
        return res
