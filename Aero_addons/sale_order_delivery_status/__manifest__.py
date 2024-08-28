{
    'name': 'Sale Order Delivery Status',
    'summary': 'Show Delivery Status on Sale Order Tree and Sale Order Form.',
    'description': 'Show Delivery Status on Sale Order Tree and Sale Order Form. Automatically update Delivery Status when stock quantity has been updated. ',
    'author': "Sonny Huynh",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['delivery', 'stock', 'sale'],

    # always loaded
    'data': [
        'security/edit_delivery_status_manually.xml',
        'views/form_view.xml',
    ],

    # only loaded in demonstration mode
    'demo': [],
    'images': [
        'static/description/banner.png',
    ],
    'license': 'OPL-1',
    'price': 65.00,
    'currency': 'EUR',
}