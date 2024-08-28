# -*- coding: utf-8 -*-
{
    'name': 'Contribution énergitique & contribution environnementale',
    'version': '1.5',
    'category': 'Sales/Sales',
    'author': 'Action Digtale',
    'website': 'https://https://action-digitale.odoo.com/',
    'summary': '',
    'sequence': -101,
    'description': """
    """,
    'depends': [
        'base',
        'account',
        'sale_management',
        'l10n_fr',
        'purchase',
    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'data/products.xml',
        # 'data/sequence_rg.xml',
        # 'views/sale_make_invoice_advance_views.xml',
        'views/sale_order_views.xml',
        # 'views/account_move_views.xml',
        'views/retenue_garantie_views.xml',
        'views/prime_cee_views.xml',
        # 'views/account_menuitem.xml',
        'views/res_partner.xml',
        'views/company_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ad_taux_contribution/static/src/components/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
