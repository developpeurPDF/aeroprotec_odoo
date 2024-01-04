# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, _

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    is_task_created = fields.Boolean(
        string='Is Task Created',
        default=False,
        copy=False,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        readonly=True,
        copy=False,
    )
    project_id=fields.Many2one(
        related="production_id.project_id",
        string='Project',
        store=True,
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        related='production_id.analytic_account_id',
        string='Analytic Account',
        store=True,
        readonly=True,
    )
    workordertask_automation = fields.Boolean(
        string='Workorder Task Automation',
        related='production_id.workordertask_automation',
    )

#     @api.multi                   #odoo13
    def button_start(self): # Override Odoo MRP method.
        result = super(MrpWorkorder, self).button_start()
        for rec in self:
            if rec.workordertask_automation:
                    task_vals = {
                        'project_id' : rec.project_id.id,
                        'name' : rec.name + '/' + rec.product_id.name,
                        'date_assign' : rec.date_start,#datetime.now(),
                        'workorder_id' : rec.id,
                        'planned_hours': rec.duration_expected / 60,
                        #'date_start': rec.date_start,
                    }
                    task_id = self.env['project.task'].create(task_vals)
                    vals = {
                        'task_id' : task_id.id,
                        'is_task_created' : True,
                    }
                    rec.write(vals)
                    #res = self.env.ref('project.action_view_task')
                    #res = res.sudo().read()[0]
                    #res['domain'] = str([('id','=',task_id.id)])
                    #return res
        return result

#     @api.multi                 #odoo13
    def show_task(self):
        #for rec in self:
        self.ensure_one()
        res = self.env.ref('mrp_workorder_task.action_view_task_mrp')
        res = res.sudo().read()[0]
        res['domain'] = str([('id','=',rec.task_id.id)])
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
