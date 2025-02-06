
# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'MRP Custom Checklist',
    'version': '16.0.0.1',
    'category': 'Manufacturing',
    'summary': 'MRP Checklist on Manufacturing checklist on MRP custom checklist on Manufacturing custom checklist on MRP own checklist Manufacturing own checklist Manufacturing order checklist mrp order checklist production checklist MO checklist workorder checklist MO',
    'description': """

        MRP Custom Checklist in odoo,
        Manufacturing Custom Checklist in odoo,
        Create Project Manufacturing in odoo,
        Create Project Manufacturing Template in odoo,
        Set Manufacturing Checklist State in odoo,
        Display Percentage in odoo,
        Checklist Progress in odoo,
        Add Checklist Template in odoo,
        Print Checklist Report in odoo,

    """,
    'author': 'BrowseInfo',
    'price': 12,
    'currency': "EUR",
    'website': "https://www.browseinfo.com/demo-request?app=bi_custom_mrp_checklist&version=16&edition=Community",
    'depends': ['base','mrp'],
    
    'data': [
        'security/ir.model.access.csv',
        'security/custom_checklist_group.xml',
        'report/manufacturing_report_inherit.xml',
        'views/manufacturing_custom_checklist_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':"https://www.browseinfo.com/demo-request?app=bi_custom_mrp_checklist&version=16&edition=Community",
    'images':["static/description/Banner.gif"],
}
