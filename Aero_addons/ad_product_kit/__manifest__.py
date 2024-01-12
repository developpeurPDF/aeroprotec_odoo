# Copyright (C) 2022 Action Digitale
# License OPL-1.0 or later
# (https://www.odoo.com/documentation/user/16.0/legal/licenses/licenses.html#).

{
    "name": "Action digitale - Product Kit",
    "summary": """Action digitale - Product Kit""",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "depends": ["product", "sale"],
    "author": "Action digitale",
    "website": "https://action-digitale.odoo.com/",
    "support": "contact@actiondigitale.net",
    "data": [
        # views
        "views/product_product_kit_view.xml",
        # security
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
    "images": ["static/description/ACTION DIGITALE.png"],
    "license": "OPL-1",
}
