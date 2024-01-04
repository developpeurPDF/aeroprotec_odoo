# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'BOM Product Cost Price',
    'version': '6.3.2',
    'category': 'Manufacturing/Manufacturing',
    'license': 'Other proprietary',
    'price': 49.0,
    'currency': 'EUR',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    # 'images': ['static/description/img.jpg'],
    'images': ['static/description/images.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_bom_product_costprice/735',#'https://www.youtube.com/watch?v=5wRFRywN0zI',
    'depends': [
            'mrp',
    ],
    'data': [
        'views/mrp_bom_views.xml',
        'views/product_views.xml',
    ],
    'summary': """BOM cost Price on Product which has BOM and Show Total Cost on BOM Form.""",
    'description': """
Bill Of Material on Product
Bill Of Material on Product Template
Bill Of Material on Product Variant
Bill of material
BOM
Product Bill Of Material
Total cost(as per BOM)
Product Cost BOM
BOM Total Cost,
Total Cost BOM
Update Product Cost from BOM
product_cost_bom
product_cost_incl_bom
Bill of Material Line Cost, Total Cost,
Bill of Material Total Cost,
Bom Cost Price Update
This module add Total Cost of Bom product.
Show BOM Total Cost on BOM
This module add total cost on BOM.
Bom Cost Total Price 
Bom Price Update
Bom Cost Total
Bom Cost Price Total
Bom Cost Update
Bom Cost Total Update
 Price Update
 Cost Price Update
bom cost price
total bom cost
bom cost
cost of bom
cost bom
BOM cost price
product bom cost
mrp cost
Manufacturing bom cost
bom Manufacturing cost
production cost bom
bom cost
    """,
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
