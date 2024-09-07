# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Custom addons MRP Aeroprotech",
    "version": "16.0.0.0",
    'description':  """ Custom addons MRP Aeroprotech
     """,
    "category": "",
    "website": "",

    "summary": "Custom addons Aeroprotech",
    'images': [''],
    "license": "LGPL-3",
    "author": "action-digitale",
    "depends": ["base","stock","sale","bom_change_version","mrp","hr","maintenance","hr_maintenance","mail","hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/parameters_matiere.xml",
        "views/product_template.xml",
        "views/model_mrp_aero.xml",
        "views/donneur_order.xml",
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
        "views/phase.xml",
        "views/machine.xml",
        "views/norme.xml",

    ],
    "application": True,
}
