{
    "name": "Report Aeroprotech",
    "version": "16.0.0.0",
    'description':  """ Report Aeroprotech
     """,
    "category": "",
    "website": "",

    "summary": "Report Aeroprotech",
    'images': [''],
    "license": "LGPL-3",
    "author": "action-digitale",
    "depends": ["base","stock","sale","bom_change_version","mrp","hr","web",],
    "data": [
        # "security/ir.model.access.csv",
        "reports/devis_commande.xml",
        "reports/layouts.xml",
        # "views/sale_order.xml",
        # "views/frais_taxe.xml",
        # "views/modes_reglement.xml",
        # "views/res_partner_invoice_total.xml",
        # "views/poids_carbone.xml",
    ],
    "assets": {

        "web.report_assets_pdf": [
            "sapa_reports/static/src/css/reports_style.scss",
        ],
    },
    "application": True,
}
