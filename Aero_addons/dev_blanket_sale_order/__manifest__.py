# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Blanket Sale Order, Sale Blanket Orders',
    'version': '16.0.1.0',
    'sequence': 1,
    'category': 'Sales',
    'description':
        """
 This Module add below functionality into odoo

        1.Blanket Sale Order\n

odoo sale Blanket order
odoo Blanket order
odoo blanket sale order
blanket sale order 
sale blanket order
order blanket in odoo 
order process in blanket 

Odoo app allow Blanket Sale Order aggreement between Seller and Customer, sale Blanket order, Blanket order, long term Sale order, Blanket Order, sale blanket


    """,
    'summary': 'Odoo app allow Blanket Sale Order aggreement between Seller and Customer, sale Blanket order, Blanket order, long term Sale order, Blanket Order, sale blanket',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/blanket_sequence_view.xml',
        'views/blanket_order_view.xml',
        'views/sale_view.xml',
        'views/customer_view.xml',
        'wizard/create_sale_quotation_view.xml',
        'data/cron_blanket_expiry_view.xml'
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':25.0,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/GOlRnho-tzI',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
