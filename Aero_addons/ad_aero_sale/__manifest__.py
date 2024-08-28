# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Custom addons sale Aeroprotech",
    "version": "16.0.0.0",
    'description':  """ Custom addons for Aeroprotech
     """,
    "category": "",
    "website": "",

    "summary": "Custom addons sale Aeroprotech",
    'images': [''],
    "license": "LGPL-3",
    "author": "action-digitale",
    "depends": ["base","stock","sale","bom_change_version","mrp","hr","maintenance","hr_maintenance","mail","hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/res_partner.xml",
        "views/frais.xml",
        "views/sale_order.xml",
    ],
    "application": True,
}
