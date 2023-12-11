# -*- coding: utf-8 -*-
{   'name': 'TekGenio Odoo Multiple ImageUploader',

    'description': """
        Simplify the task of uploading product images into your Odoo database with our cutting-edge Solution.
        Sync your all Odoo Product Images directly from your computer with our efficient Solution.                              
    """,
    'currency': 'USD',
    'price': 100,
    'license': 'OPL-1',

    'author': "TekGenio",
    'website': "https://tekgenio.com",
    'images': ['static/description/banner.png'],
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','stock','website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/product_template_clean_images.xml',
        # 'views/folder_update_views.xml',
        'views/log_views.xml',
        'views/res_config.xml',
        'views/product_template_views.xml',
    ],

    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
    'uninstall_hook': 'uninstall_hook',
}
