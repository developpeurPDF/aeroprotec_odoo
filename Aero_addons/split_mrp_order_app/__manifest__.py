# -*- coding: utf-8 -*-

{
    "name" : "Manufacturing Orders Splitting Apps",
    "author": "Edge Technologies",
    "version" : "16.0.1.0",
    "live_test_url":'https://youtu.be/SbjLA9-eiuY',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Split MRP splitting manufacturing order split production order splitting manufacturing splitting MRP split manufacturing order line split MRP line manufacturing order separation partial manufacturing split process separate MRP line MRP split process.',
    "description": """Split manufacturing order odoo apps use for split manufacturing by number of quantity and by number of MO splitting from current order.
    """,
    "license" : "OPL-1",
    "depends" : ['mrp'],
    "data": [
            'security/allow_split_order.xml',
            'security/ir.model.access.csv',
            'wizard/confirm_split_order.xml',
            'views/split_view.xml',      
    ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": 'EUR',
    'category': 'Manufacturing',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
