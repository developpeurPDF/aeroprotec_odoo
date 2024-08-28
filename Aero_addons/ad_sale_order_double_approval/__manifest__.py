# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Double Approval',
    
    'author' : 'Action Digitale',
    
    'website': 'https://action-digitale.odoo.com/',
      
        
    'version': '16.0.0',
    
    'category': 'Sales',

    'summary': """
 Sale Order Double Approval, SO Double Approval, Sales Order Double Validation Module


""",

    'description': """Not all humans are professional. It does not matter how clever, trusted or trained we are, sooner or later everybody will make a mistake. That's why we make this module. As the name implies, Double Approval is a control that requires two separate people to authorize a transaction. The first person is responsible for creating the request (known as the user), while the second person checks and approves the activity (known as the manager). Double Approval clearly helps protect your business, but it also helps protect your employees from making a mistake from the process. This module will help to set a limit of the sale order amount for the user, If a user makes a sale order beyond the limit, So that sale order automatically sets in the 'To Approve' stage. And then the manager can approve or refuse this sale order from 'Sale Order Approval'. This module can help to track approved or refused orders with approved by, refused by, approved date, refusal date, refusal reason. You can alert for approving via email to the sales team, specific user, or that person who has to approve limit more than a sale order amount.
 Sale Order Double Approval Odoo
""",
    
    'depends': ['sale_management','versioning_in_sale_order'],
    
    'data': [
            'security/ir.model.access.csv',
            'data/sale_order_double_approval_group.xml',
            'data/sale_order_double_approval_template.xml',
            'views/sale_config_settings.xml',
            'views/res_users.xml',
            'views/sale_order.xml',
            'views/sale_order_approval.xml',
            'views/sh_so_refuse_reason.xml',
            'wizard/sh_refuse_reason_wizard.xml',
            ],

    'images': ['static/description/background.png',],              
    'auto_install': False,
    'installable' : True,
    'application': True,           
}
