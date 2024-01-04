# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name':'Print Manufacturing Order Barcode/Lot',
    'price': 90.0,
    'version':'6.3.2',
    'category': 'Manufacturing/Manufacturing',
    'currency': 'EUR',
    'summary': 'This module print lot barcode from Manufacturing Order for Raw materials and Finished product.',
    'license': 'Other proprietary',
    'description': """
MRP - Print Lot Label Report. This module allow print product barcode and company information on lot barcode.
Report Label Lot
Product Barcode
Product Quantity
Print Report Label Lot
Print Lot Label
MRP Lot Barcode
Report Label Lot
Product Barcode
Product Quantity
Print Report Label Lot
barcode print
print barcode
print barcode
ean13
barcode lable print
barcode print lot
lot print
print lot number
print lot barcode
print barcode lot
barcode printing
lot number
lot printer
printer lot number
printer barcode
barcode printer
lot print report
pdf lot barcode
barcode pdf report
barcode pdf
printer barcode
product barcode print
print product barcode
Lot/Serial Number
lot print
serial number print
print serial number barcode
serial number barcode
mrp lot number
manufacturing lot number
mrp barcode
production barcode
mrp lot barcode
mrp lot
production lot barcode
production lot
manufacturing lot print
manufacturing barcode print

            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'images': ['static/description/img1.png'],
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/mk-mY9eAXPM',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/mrp_print_lot_label/142',#'https://youtu.be/9GtH5Sp1ZoY',
     #'https://youtu.be/q5Hq9RETknY',
    'depends': [
         'mrp'
    ],
    'data':[
             'data/report_paperformat.xml',
             'report/report_label_workorder.xml',
             'views/mrp_production_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
