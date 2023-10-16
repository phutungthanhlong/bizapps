# -*- coding: utf-8 -*-
# Part of TechUltra Solutions. See LICENSE file for full copyright and licensing details.
{
    'name': 'Pricelists Grade',
    'summary': """
    Sales Pricelists according to the grade
    """,
    'description': """
    Assign Sales Pricelists according to the selected grade of the customer
    """,
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': 'http://www.techultrasolutions.com',
    'category': 'Sales',
    'version': '16.0.1',
    'license': 'AGPL-3',
    'depends': ['base', 'product', 'sale_management'],
    'data': [
        "security/ir.model.access.csv",
        "views/grade_product_pricelist.xml",
        "views/res_partner.xml",
        "views/product_pricelist.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "images": [
        "static/description/main_screen.gif",
    ],

}
