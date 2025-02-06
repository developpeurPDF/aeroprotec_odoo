# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name' : "Système de gestion des accès",
    
    "author": "Action Digitale",

    "license": "OPL-1",

    "website": "https://action-digitale.odoo.com/",

    "support": "contact@actiondigitale.net",

    "version": "16.0.1",

    "category": "Extra Tools",

    "summary": "",

    "description": """""",

    'depends' : ['base_setup','web','base','sale_management','mail'],

    'data' : [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/access_manager.xml',
        'views/sale_order.xml',
    ],

    'assets': {    
        'web.assets_backend': [
            'ad_access_management/static/src/js/hide_multiactions.js',
            'ad_access_management/static/src/js/chatter_container.js',
            'ad_access_management/static/src/xml/ad_create_access.xml',
            'ad_access_management/static/src/xml/chatter_container.xml',
        ],   
        
    },
    'demo' : [],
    'installation': True,
    'application' : True,
    'auto_install' : False,
    "images": ["static/description/background.png", ],
    'icon': 'ad_access_management/static/description/ad_icon.png',

}
