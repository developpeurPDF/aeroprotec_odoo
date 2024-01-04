# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Odoo Manufacturing WorkOrder Integration Task",
    'price': 50.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/mrp_workorder_task/1030',#'https://youtu.be/z4foIT3gjyQ',
    'summary': """This module will create tasks from manufacturing work-orders.""",
    'description': """
Manufacturing WorkOrder Integration Task
This module will create tasks from manufacturing work-orders.

work order task
workorder task
Manufacturing task
task on workorder
workorder on tasks
project task for Manufacturing
project task for workorder
task for job order
task for joborder
job order
joborder
work order
mrp work order
mrp task
mrp_task
Manufacturing workorder 
Manufacturing joborder
job task for user
project on Manufacturing
Manufacturing project
analytic account Manufacturing order
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'version': '3.23.1',
    'category' : 'Manufacturing',
    'depends': ['mrp', 'project','hr_timesheet'],
    'data':[
        'views/mrp_production.xml',
        'views/mrp_workorder.xml',
        'views/project_task.xml',
        'report/workorder_report.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
