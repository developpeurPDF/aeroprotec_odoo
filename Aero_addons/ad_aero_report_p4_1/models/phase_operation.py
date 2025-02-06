from odoo import api, fields, models

class SousOperation(models.Model):
    _inherit = 'phase.operation'

    workorder_ids = fields.Many2many(
        'mrp.workorder',
        'workorder_phase_rel',
        'phase_id',
        'workorder_id',
        string="Opération d'ordre de travail"
    )
