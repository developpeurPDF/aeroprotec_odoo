{
    "name": "Non Conformité",
    "version": "16.0.0.0",
    'description':  """ Non Conformité
     """,
    "category": "",
    "website": "",

    "summary": "Non conformité",
    'images': [''],
    "license": "LGPL-3",
    "author": "action-digitale",
    "depends": ["base","mrp","mrp_quality_control_app","warehouse_quality_control_app"],
    "data": [
        "security/ir.model.access.csv",
        "views/non_conformite.xml",
        "views/type_defaut_views.xml",
        "views/cause_non_conformite_views.xml",
        "views/maintenance_request.xml",
        #"views/menu.xml",
        'data/sequence.xml',
        'views/quality_checks.xml',
        'views/quality_point_equipment.xml',
    ],

    'installable': True,
    'application': True,
    "images": ["static/description/ad_icon.png",],
    'icon': 'ad_aero_non_conformite/static/description/ad_icon.png',
}