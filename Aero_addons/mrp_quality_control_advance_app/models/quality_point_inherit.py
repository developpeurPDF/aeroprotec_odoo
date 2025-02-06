# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _



class Quality_check(models.Model):
	
	_inherit = 'quality.checks'

	product_tracking = fields.Selection(related="product_id.tracking")
	mrp_check = fields.Boolean('Contrôle de qualité')

