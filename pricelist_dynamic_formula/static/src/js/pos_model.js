/* global waitForWebfonts */
odoo.define('custom_point_of_sale.models', function (require) {
"use strict";

    var { Product } = require('point_of_sale.models');
    const { patch } = require('@web/core/utils/patch');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    patch(Product.prototype, "pos_product", {

        get_price(pricelist, quantity, price_extra) {
            var self = this;
            var date = moment();

            if (!pricelist) {
                alert(_t(
                    'An error occurred when loading product prices. ' +
                    'Make sure all pricelists are available in the POS.'
                ));
            }

            var pricelist_items = _.filter(
                self.applicablePricelistItems[pricelist.id],
                function (item) {
                    return self.isPricelistItemUsable(item, date);
                }
            );

            var price = self.lst_price;
            if (price_extra){
                price += price_extra;
            }
            _.find(pricelist_items, function (rule) {
                if (rule.min_quantity && quantity < rule.min_quantity) {
                    return false;
                }
                if (rule.base === 'pricelist') {
                    let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
                        return pricelist.id === rule.base_pricelist_id[0];});
                    if (base_pricelist) {
                        price = self.get_price(base_pricelist, quantity);
                    }
                } else if (rule.base === 'standard_price') {
                    price = self.standard_price;
                }

                if (rule.compute_price === 'fixed') {
                    price = rule.fixed_price;
                    return true;
                } else if (rule.compute_price === 'percentage') {
                    price = price - (price * (rule.percent_price / 100));
                    return true;
                } else {
                    if (rule.compute_price === 'dynamic_formula') {
                        price = JSON.parse(rule.list_product_price)[self.id] || price;

                    } else {
                        var price_limit = price;
                        price = price - (price * (rule.price_discount / 100));
                        if (rule.price_round) {
                            price = round_pr(price, rule.price_round);
                        }
                        if (rule.price_surcharge) {
                            price += rule.price_surcharge;
                        }
                        if (rule.price_min_margin) {
                            price = Math.max(price, price_limit + rule.price_min_margin);
                        }
                        if (rule.price_max_margin) {
                            price = Math.min(price, price_limit + rule.price_max_margin);
                        }
                        return true;
                    }
                }
                return false;
            });
            return price;
        },

    });
});