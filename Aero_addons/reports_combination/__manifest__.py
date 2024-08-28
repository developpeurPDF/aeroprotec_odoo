{
    "name": "Add CGV to sale report",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "summary": "Add CGV to QWEB invoice PDF reports",
    "depends": ["web", "account","sale","base","sale_management"],
    "data": [
        "views/sale_order_template_inherit_view.xml",
        "views/sale_order_inherit_view.xml",
        "reports/report_invoice.xml",
        "reports/account_report.xml",
        "data/sale_order_template_data.xml",
    ],
    "installable": True,
 #   "external_dependencies": {"python": ["PyPDF2"]},
}
