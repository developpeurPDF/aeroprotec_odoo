

{
    'name': 'OpenBee Connector',
    'version': '1.0',
    'author': 'Action Digitale',
    'description': """
            This module adds integration with OpenBee Document Management System:
            - Send invoices to OpenBee
            - Track OpenBee document IDs
        """,
    'depends': ['base','account', 'sale', 'purchase','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/openbee_connector.xml',
        'views/account_move_views.xml',
        'views/parametre_openbee.xml',
        'views/res_partner.xml',
        'views/sale_order_view.xml',
        'views/mrp_production.xml',
        'views/purchase_order.xml',
        # 'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
