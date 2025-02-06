# -*- coding: utf-8 -*-
{
    'name': 'Odoo Metabase Connector',
    'author': 'Softprime Consulting Pvt Ltd',
    'maintainer': 'Softprime Consulting Pvt Ltd',
    'website': 'https://softprimeconsulting.com/',
    'version': '16.0.1.0.0',
    "support": "info@softprimeconsulting.com",
    "company": "Softprime Consulting Pvt Ltd",
    "license": "OPL-1",
    "currency": "USD",
    "price": "14.99",
    'category': 'Dashboard',
    'summary': 'Management Metabase dashboards.',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/metabase_configuration.xml',
        'views/metabase_dashboard.xml',
        'menu/menu.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'sp_odoo_metabase_connector/static/src/js/*.js',
            'sp_odoo_metabase_connector/static/src/xml/*.xml',
        ]
    },
    'images': ['static/description/banner.jpeg'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
