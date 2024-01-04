# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Odoo Backend Theme Main Menu",
    'currency': 'EUR',
    'license': 'Other proprietary',
    'price': 19.0,
    'summary': """Home Menu Backend Theme Odoo Apps""",
    'description': """
This app provides the theme of fullscreen for apps in community edition.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/theme_image.jpg'],
    'version': '1.1.1',
    'category' : 'Sales/Sales',
    'depends': ['web'],
    'data':[
    ],
    'assets': {
        'web.assets_backend': [
            'theme_backend_odoo_comm/static/src/scss/custom_theme.scss',
            'theme_backend_odoo_comm/static/src/navbar/navbar_menu.js',
            'theme_backend_odoo_comm/static/src/navbar/navbar_menu.xml',
        ],
    },
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
