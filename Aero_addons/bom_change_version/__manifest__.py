# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Engineering Change Order (ECO) for BOM',
    'version': '4.4.5',
    'price': 29.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    # 'category' : 'Manufacturing',
    'category': 'Manufacturing/Manufacturing',
    'summary': """This app provide feature of engineering change order (ECO) for Bill of Materials""",
    'description': """
Engineering Change Orders
BOM Change Order
Current Version on BOM
BOM Change Order Processed
Bill of Material - BOM Change Order
BOM Change Order Validated,
Activate BOM
Activated New BOM on BOM Change Order
Original Bill of Material Archived
BOM Change Order PDF Report
Engineering Change Order
BOM Change Order - BOM Version
ECO
engineering change order
ECO
bom
bill of material
Product Change Management
ECR
Engineering change request
Change implementation
Change Management
Engineering Change Notice
ECN
change management process
engineering change request
Engineering Change Proposal
ECP
Engineering change orders
engineering change
assemblies
components
work instructions
Engineering Change Management
Master production schedule
Engineering Change Order Process
Engineering Change Order Revision
bom revision
bom revise
revise bom
bill of material revision
Workbench
change order
Manufacturing process
Production Bill of Material (BOM)
Production
Bill of Material
Manufacturing
bill of materials revision
change order

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
#    'live_test_url': 'https://youtu.be/G7v_MU-U0a8', old
    # 'live_test_url': 'https://youtu.be/hl27Vb52Zv8',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/bom_change_version/266',#'https://youtu.be/qaJFRqLpsIs',
    'depends': [
               'mrp'
                ],
    'data':[
       'datas/bom_change_sequence.xml',
       'security/bom_change_order_security.xml',
       'security/ir.model.access.csv',
       'views/bom_change_version_view.xml',
       'views/mrp_bom_views.xml',
       'views/report_bom_change_version.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
