# -*- coding: utf-8 -*-

from odoo import fields, models, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        readonly=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )

    analytic_account_id = fields.Many2one(
        related='project_id.analytic_account_id',
        string='Analytic Account',
        readonly=True,
        store=True,
    )
    
    workordertask_automation = fields.Boolean(
        string='Workorder Task Automation',
        default=True,
        readonly=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Tick this box if you want to create task aumatically when job order will start."
    )

#     @api.multi              #odoo13
    def view_task(self):
        #for rec in self:
        self.ensure_one()
        res = self.env.ref('mrp_workorder_task.action_view_task_mrp')
        res = res.sudo().read()[0]
        res['domain'] = str([('mrp_id','=',self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
