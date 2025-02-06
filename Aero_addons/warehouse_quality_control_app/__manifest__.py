# -*- coding: utf-8 -*-
{
    'name': 'Inventory Quality Control Management in Odoo',
    "author": "Edge Technologies",
    'version': '16.0.1.0',
    'live_test_url': "https://youtu.be/1VgJKTJCx5U",
    "images":['static/description/main_screenshot.png'],
    'summary': "Quality control for warehouse quality control for inventory quality control inspection qc warehouse QC validation WMS quality assurance inventory quality control inventory inspection purchase quality control purchase inspections quality inspection alerts.",
    'description': """This app help to user for quality control like quality check and quality alert for warehouse. also generate quality check and alert report.

Quality Control Inspections
Internal Validation and Verification
QC features of warehouse management
QC warehouse management
QA warehouse management
WMS QUALITY ASSURANCE
Quality control
WMS Quality assurance
QUALITY CONTROL WMS
Inventory Control and Quality Control
Inventory Quality Control
Quality Control Inventory 
Quality Control Management
Inventory control
warehouse quality control
 Inventory Management 
 Stock Control and Inventory Management
 Warehouse quality control
 Warehouse Performance Management
 Improve Quality and Productivity in Warehouse Operations
 Warehouse Operations - Quality Inspection
 Quality Inspection
 Quality Systems Warehouse Management
 Quality Assurance
 Quality management
 Quality Management in Warehouse Management
 Stock control
 Inventory cost management
 Multiple location support
 Inventory control systems
Purchase Product Quality Instpection
Quality alerts and Quality Inspections
Incoming Product Quality Instpection
Inventory inspection
Shipment inspection
Pre-shipment inspection
Shipment inspection
Pre Shipment Inspection

Quality control inspections 
Product quality control inspections 
WMS quality control inspections 
Warehouse quality control inspections 
Quality Control and Preshipment Inspection
Warehouse quality audit checklist
Quality Management
Purchase quality control management
Picking quality control management
Delivery quality control management
Incoming shipment quanlity control management
Quality control team
Quality control alerts
Quality control points
Purchase quality Inspection management
Picking quality Inspection management
Delivery quality Inspection management
Incoming shipment quanlity Inspection management
Quality Inspection team
Quality Inspection alerts
Quality Inspection points
Warehouse QC control qc Control team purchase qc management warehouse qc management picking qc management
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','stock','purchase','account','hr'],
    'data': [
            'security/ir.model.access.csv',
            'wizard/wizard_views.xml',
            'views/quality_point.xml',
            'views/picking_inherit.xml',
            'views/quality_team_viewe.xml',
            'views/quality_alert_view.xml',
            'views/cause_occurrence_views.xml',
            'views/cause_non_detection_views.xml',
            'report/check_quality_reports.xml'
            ],
    'installable': True,
    'auto_install': False,
    'price': 75,
    'currency': "EUR",
    'category': 'Extra Tools',

}

