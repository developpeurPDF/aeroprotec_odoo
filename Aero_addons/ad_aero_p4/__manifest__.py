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
    "depends": ["base","stock","sale","bom_change_version","mrp","hr","web","ad_aero_custom_addons","ad_aero_sale"],
    "data": [

        "security/ir.model.access.csv",
        "views/ordonancement.xml",
        "views/peinture_melange.xml",
        "views/application_peinture.xml",
        "views/mrp_workorder.xml",
        "views/etuvage_views.xml",
        "views/hr_employee.xml"

    ],
    "assets": {

        "web.report_assets_pdf": [
            "sapa_reports/static/src/css/reports_style.scss",
        ],
    },
    "application": True,
}
