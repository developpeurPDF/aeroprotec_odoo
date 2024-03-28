# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    bom_temp_id = fields.Many2one(
        'mrp.bom.template', 'Parent BoM',
        index=True, ondelete='cascade') #, required=True