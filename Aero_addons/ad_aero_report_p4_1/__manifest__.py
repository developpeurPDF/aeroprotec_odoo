{
    "name": "Rapport AEROPROTC",
    "version": "16.0.0.0",
    'description':  """ Rapport AEROPROTC
     """,
    "category": "",
    "website": "",

    "summary": "Rapport AEROPROTC",
    'images': [''],
    "license": "LGPL-3",
    "author": "action-digitale",
    "depends": ["base","mrp","ad_aero_custom_addons"],
    "data": [
        #'security/ir.model.access.csv',
        "reports/header_fiche_suivi.xml",
        "reports/fiche_suivi_footer.xml",
        "reports/control_report_template.xml",
        "reports/control_libertoire_final.xml",
        "reports/reports_action.xml",
        "reports/pv_cnd_report_template.xml",
        "reports/fiche_suivi-report_template.xml",
        "reports/bon_livraison_tempate.xml",
        "reports/ordre_travail_template.xml",
        "reports/certificat_conformite_report_template.xml",

        "data/report_paperformat.xml",
        "data/fiche_suivi_paperformat.xml",
        #"views/mrp_workorder.xml",
        #"views/phase_operation_views.xml",
        "views/mrp_production.xml",
        "views/stock_picking_view.xml",
        "views/layouts.xml",
        'views/mrp_popup_wizard_views.xml',
        'views/actions.xml',



    ],
    "assets": {

        "web.report_assets_pdf": [
            "sapa_reports/static/src/css/style.css",
        ],
    },
    "application": True,
}
