# -*- coding: utf-8 -*-
{
    'name': 'BoM operation template, manufacture operations templates',
    'summary':'You can create your Bill of Materials and add operations by prepared operation templates.',
    'category': 'Manufacturing',
    'version': '15.0',
    'sequence': 1,
    "author": "Unicoding.by",
    "website": "https://unicoding.by",
    'depends': ['base','mrp'],
    "license": "AGPL-3",
    'data': [
            'security/ir.model.access.csv',
            'view/routes_template_view.xml',
            'view/mrp_bom_view.xml',
             ],
    'installable': True,
    'images':[
        'static/description/0.png',
    ],
    "price": 39.99,
    'currency': 'EUR',
}
