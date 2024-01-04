# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = "project.task"

    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Work Order',
        readonly=True,
    )
    mrp_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        related='workorder_id.production_id',
        store=True,
    )
    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        string='Work Center',
        related = 'workorder_id.workcenter_id',
        readonly=True,
    )
    worksheet = fields.Binary(
        string='Worksheet',
        related='workorder_id.worksheet',
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

