# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "MRP Operation Worsheets | MRP Operations Additional Work Sheets | MRP Additional Work Sheets",
    "summary": """
        Your module enables Odoo users to add additional worksheets to MRP operations. When a work order is created, these extra worksheets become available to users.
    """,
    "version": "16.1",
    "description": """
        Your module enables Odoo users to add additional worksheets to MRP operations. When a work order is created, these extra worksheets become available to users.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/mrp_routing_worksheets.png"],
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_routing_worksheets_views.xml",
        "views/mrp_workorder_views.xml",
    ],
    "assets": {
        "web.assets_backend": [

        ],
    },
    "installable": True,
    "application": True,
    "price"                 :  40.00,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
