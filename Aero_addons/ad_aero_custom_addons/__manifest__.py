# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "ad_aero_custom_addons",
    "version": "16.0.0.0",
    'description':  """ Custom addons for Aeroprotech
     """,
    "category": "",
    "website": "",

    "summary": "Custom addons Aeroprotech",
    'images': [''],
    "license": "LGPL-3",
    "author": "action-digitale",
    "depends": ["base","stock","sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/parameters_matiere.xml",
        "views/product_template.xml",
        "views/model_mrp_aero.xml"
        # "report/print.xml",
        # "report/account_move.xml",


    ],
    "application": True,
}
