# -*- coding: utf-8 -*-
{
	'name': 'Manufacturing BOM Template | MRP Bill of Materials | BOM Template for Manufacturing | Manufacturing Template | MRP Template',
	"author": "Edge Technologies",
	'version': '16.0.1.0',
	'live_test_url': "https://youtu.be/ENEdtS3E1_8",
	"images":['static/description/main_screenshot.png'],
	'summary': "Create bill of material template MRP BOM template manufacturing template bill of materials MRP template manage bill of material manufacturing order template for BOM template for MRP orders template bill of materials MRP order bill of materials template",
	'description': """ 
        Create Bill of Material from it and we can easily create Bill of Material from it
	""",
	"license" : "OPL-1",
	'depends': ['base','mrp','ad_aero_custom_addons'],
	'data': [
			'security/ir.model.access.csv',
			'data/ir_sequence_data.xml',
			'views/inherit_mrp_bom.xml',
			'views/mrp_bom_temp.xml'
			],
	'installable': True,
	'auto_install': False,
	'price': 10,
	'currency': "EUR",
	'category': 'manufacturing',
}