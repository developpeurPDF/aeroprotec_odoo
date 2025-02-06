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
    "depends": ["base","stock","sale","bom_change_version","mrp","hr","maintenance",
                "hr_maintenance","mail","hr","account","ad_taux_contribution"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
        "views/frais_taxe.xml",
        "views/modes_reglement.xml",
        "views/res_partner_invoice_total.xml",
        "views/poids_carbone.xml",
        "wizards/controle_qualite_reception.xml",
        "views/stock_picking.xml",
        "views/product_price_list_period.xml",
        "report/control_recption.xml"

    ],
    "application": True,
}
