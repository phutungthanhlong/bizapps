# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Product Price Calculation',
    'summary': 'Dynamic Product Price Calculation',
    'version': '16.1.1.0',
    'category': 'Sale',
    'website': 'https://winerp.vn',
    'description': 'Dynamic Product Price Calculation',
    'images':[],
    'author': 'Odoo Việt Nam - WINERP',
    'support': 'info@winerp.vn',
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist_item_views.xml',
    ],
    'depends': ['product', 'sale', 'point_of_sale'],
    'qweb': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'point_of_sale.assets': [
            'pricelist_dynamic_formula/static/src/**/*.js',
        ],
    },
}
