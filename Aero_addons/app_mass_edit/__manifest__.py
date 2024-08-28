# -*- coding: utf-8 -*-

# Created on 2019-01-04
# author: 欧度智能，https://www.odooai.cn
# email: 300883@qq.com
# resource of odooai
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo12在线用户手册（长期更新）
# https://www.odooai.cn/documentation/user/12.0/en/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.odooai.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.odooai.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.odooai.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.odooai.cn/odoo10_developer_document_offline/

{
    'name': 'Mass Edit with easy 1 click button,批量编辑',
    'version': '16.23.09.26',
    'contributors': [
        'Serpent Consulting Services Pvt. Ltd.',
        'Tecnativa',
        'GRAP',
        'Iván Todorovich',
        'Odoo Community Association (OCA)'
    ],
    'author': 'odooai.cn',
    'category': 'Base',
    'website': 'https://www.odooai.cn',
    'live_test_url': 'https://demo.odooapp.cn',
    'license': 'OPL-1',
    'summary': 'Mass Editing, mass edit, Batch edit, quick edit, Batch Edit Multi Records in all models,',
    'uninstall_hook': 'uninstall_hook',
    'price': 38.00,
    'currency': 'EUR',
    'images': ['static/description/banner.gif'],
    'depends': [
        'web',
        'app_common',
        'app_odoo_customize'
    ],
    'description': '''    
    Support Odoo 16,15,14,13,12, Enterprise and Community Edition
    1. Mass Edit multi  Record in 1 Click 
    2. Easy set Mass edit for all app, all models, all field
    3. Multi-language Support.
    4. Multi-Company Support.
    5. Support Odoo 16,15,14,13,12, Enterprise and Community Edition
    ==========
    1. 一键批量更新记录
    2. 可定制化odoo各应用，各模型
    3. 多语言支持
    4. 多公司支持
    5. Odoo 16,15,14,13,12, 企业版，社区版，多版本支持
    ''',
    'data': [
        'security/ir.model.access.csv',
        'views/ir_actions_server.xml',
        'views/menu_views.xml',
        'wizard/mass_editing_wizard.xml',
    ],
    "demo": ["demo/mass_editing.xml"],
    'installable': True,
    'application': False,
    'auto_install': False,
    "uninstall_hook": None,
}
