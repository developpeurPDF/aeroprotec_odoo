# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.depends('direct_material_byproduct_ids','overhead_cost_byproduct_ids','labour_cost_byproduct_ids')
    def _compute_material_total_byproduct(self):
        for rec in self:
            rec.material_total_byproduct = sum([p.total_cost for p in rec.direct_material_byproduct_ids])
            rec.overhead_total_byproduct = sum([p.total_cost for p in rec.overhead_cost_byproduct_ids])
            rec.labor_total_byproduct = sum([p.total_cost for p in rec.labour_cost_byproduct_ids])
            
    direct_material_byproduct_ids = fields.One2many(
        'bom.job.cost.line.byproduct',
        'bom_byproduct_id',
        string="Direct Material",
        domain=[('job_type','=','material')],
    )
    labour_cost_byproduct_ids = fields.One2many(
        'bom.job.cost.line.byproduct',
        'bom_byproduct_id',
        string="Direct Material",
        domain=[('job_type','=','labour')],
    )
    overhead_cost_byproduct_ids = fields.One2many(
        'bom.job.cost.line.byproduct',
        'bom_byproduct_id',
        string="Direct Material",
        domain=[('job_type','=','overhead')],
    )
    material_total_byproduct = fields.Float(
        string='Total Material Cost',
        compute='_compute_material_total_byproduct',
        store=True,
    )
    overhead_total_byproduct = fields.Float(
        string='Total Overhead Cost',
        compute='_compute_material_total_byproduct',
        store=True,
    )
    labor_total_byproduct = fields.Float(
        string='Total Labour Cost',
        compute='_compute_material_total_byproduct',
        store=True,
    )
    custom_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.user.company_id.currency_id, 
        string='Currency',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
