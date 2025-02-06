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
    "depends": ["base","stock","sale","mrp","hr","web",],
    "data": [
        "reports/mrp_ordre_de_fabrication_report.xml",
        "views/mrp_production.xml",
        "reports/parametre.xml",
    ],
    "assets": {

        "web.report_assets_pdf": [
            "sapa_reports/static/src/css/reports_style.scss",
        ],
    },
    "application": True,
}
