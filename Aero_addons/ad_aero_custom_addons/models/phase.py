from odoo import api, fields, models, _
from math import pi

class PhaseOperation(models.Model):
    _name = 'phase.operation'

    name = fields.Char(string="Phase d'opération")
    company_id = fields.Many2one('res.company', string="Société")
    operations = fields.One2many('mrp.routing.workcenter', 'phase', string="Opérations")

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    phase = fields.Many2one('phase.operation', string="Phase d'opération")