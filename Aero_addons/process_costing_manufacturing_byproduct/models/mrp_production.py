# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.depends('material_total_byproduct','labor_total_byproduct','overhead_total_byproduct')
    def _compute_total_final_cost_byproduct(self):
        for rec in self:
            rec.final_total_cost_byproduct = rec.material_total_byproduct + rec.labor_total_byproduct + rec.overhead_total_byproduct
            #rec.final_total_actual_cost = rec.total_actual_material_cost + rec.total_actual_labour_cost + rec.total_actual_overhead_cost
    #@api.one
    @api.depends(
        'direct_material_byproduct_ids',
        'overhead_cost_byproduct_ids',
        'labour_cost_byproduct_ids',
        'direct_material_byproduct_ids.total_cost',
        'overhead_cost_byproduct_ids.total_cost',
        'labour_cost_byproduct_ids.total_cost',
        )
    def _compute_material_total_byproduct(self):
        self.material_total_byproduct = sum([p.total_cost for p in self.direct_material_byproduct_ids])
        self.overhead_total_byproduct = sum([p.total_cost for p in self.overhead_cost_byproduct_ids])
        self.labor_total_byproduct = sum([p.total_cost for p in self.labour_cost_byproduct_ids])
        
            
    direct_material_byproduct_ids = fields.One2many(
        'mrp.job.cost.line.byproduct',
        'mrp_id',
        string="Direct Material",
        domain=[('job_type','=','material')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    labour_cost_byproduct_ids = fields.One2many(
        'mrp.job.cost.line.byproduct',
        'mrp_id',
        string="Direct Material",
        domain=[('job_type','=','labour')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    overhead_cost_byproduct_ids = fields.One2many(
        'mrp.job.cost.line.byproduct',
        'mrp_id',
        string="Direct Material",
        domain=[('job_type','=','overhead')],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self: self.env.user.company_id.currency_id, 
        string='Currency', 
        readonly=True
    )
    
    #@api.one
    @api.depends(
        'direct_material_byproduct_ids',
        'overhead_cost_byproduct_ids',
        'labour_cost_byproduct_ids',
        'direct_material_byproduct_ids.total_actual_cost',
        'overhead_cost_byproduct_ids.total_actual_cost',
        'labour_cost_byproduct_ids.total_actual_cost',
        )
    def _compute_total_actual_cost(self):
        for rec in self:
            rec.total_actual_material_cost = sum([p.total_actual_cost for p in rec.direct_material_byproduct_ids])
            rec.total_actual_labour_cost = sum([p.total_actual_cost for p in rec.labour_cost_byproduct_ids])
            rec.total_actual_overhead_cost = sum([p.total_actual_cost for p in rec.overhead_cost_byproduct_ids])

    total_actual_labour_cost = fields.Float(
        string='Total Actual Labour Cost',
        compute='_compute_total_actual_cost',
        store=True,
    )
    total_actual_material_cost = fields.Float(
        string='Total Actual Material Cost',
        compute='_compute_total_actual_cost',
        store=True,
    )
    total_actual_overhead_cost = fields.Float(
        string='Total Actual Overhead Cost',
        compute='_compute_total_actual_cost',
        store=True,
    )
    labor_total_byproduct = fields.Float(
        string='Total Labour Cost By Product',
        compute='_compute_material_total_byproduct',
        store=True,
    )
    overhead_total_byproduct = fields.Float(
        string='Total Overhead Cost By Product',
        compute='_compute_material_total_byproduct',
        store=True,
    )
    material_total_byproduct = fields.Float(
        string='Total Material Cost By Product',
        compute='_compute_material_total_byproduct',
        store=True,
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self: self.env.user.company_id.currency_id, 
        string='Currency', 
        readonly=True
    )
    final_total_cost_byproduct = fields.Float(
        string='Total Cost By Product',
        compute='_compute_total_final_cost_byproduct',
        store=True,
    )

    @api.model
    def create(self, vals):
        result = super(MrpProduction, self).create(vals)
        if not result.bom_id:
            return result
        material_list = []
        labour_list = []
        overhead_list = []
        job_cost_obj = self.env['mrp.job.cost.line.byproduct']
        
        for material in result.bom_id.direct_material_byproduct_ids:
               material_vals = {'routing_workcenter_id': material.routing_workcenter_id.id, 
                      'product_id': material.product_id.id, 
                      'product_qty': (result.product_qty * material.product_qty) / result.bom_id.product_qty,
                      'job_type':'material',
                      'uom_id': material.uom_id.id,
                      'cost_price': material.cost_price,
                      'total_cost': material.total_cost,
                      'actual_quantity': (result.product_qty * material.product_qty) / result.bom_id.product_qty,
                      'mrp_id':result.id
                      }
               job_cost_obj.create(material_vals)
                
        for labour in result.bom_id.labour_cost_byproduct_ids:
                labour_vals = {'routing_workcenter_id': labour.routing_workcenter_id.id, 
                      'product_id': labour.product_id.id, 
                      'product_qty': (result.product_qty * labour.product_qty) / result.bom_id.product_qty,
                      'job_type':'labour',
                      'uom_id': labour.uom_id.id,
                      'cost_price': labour.cost_price,
                      'total_cost': labour.total_cost,
                      'actual_quantity': (result.product_qty * labour.product_qty) / result.bom_id.product_qty,
                      'mrp_id':result.id
                      }
                job_cost_obj.create(labour_vals)

        for overhead in result.bom_id.overhead_cost_byproduct_ids:
                overhead_vals = {'routing_workcenter_id': overhead.routing_workcenter_id.id, 
                      'product_id': overhead.product_id.id, 
                      'product_qty': (result.product_qty * overhead.product_qty) / result.bom_id.product_qty,
                      'job_type':'overhead',
                      'uom_id': overhead.uom_id.id,
                      'cost_price': overhead.cost_price,
                      'total_cost': overhead.total_cost,
                      'actual_quantity': (result.product_qty * overhead.product_qty) / result.bom_id.product_qty,
                      'mrp_id':result.id
                      }
                job_cost_obj.create(overhead_vals)
        return result
        
    #@api.multi
    def write(self, vals):
        rec = super(MrpProduction, self).write(vals)
        if vals.get('product_qty'):
            for order in self:
                for bom_material in order.bom_id.direct_material_byproduct_ids:
                    material_id = order.direct_material_byproduct_ids.filtered(lambda material: material.product_id == bom_material.product_id)
                    if material_id:
                        for material in material_id:
                            material.product_qty = (bom_material.product_qty * order.product_qty) / order.bom_id.product_qty
                            material.actual_quantity = (bom_material.product_qty * order.product_qty) / order.bom_id.product_qty
                
                for bom_labour in order.bom_id.labour_cost_byproduct_ids:
                    labour_id = order.labour_cost_byproduct_ids.filtered(lambda labour: labour.product_id == bom_labour.product_id)
                    if labour_id:
                        for labour in labour_id:
                            labour.product_qty = (bom_labour.product_qty * order.product_qty) / order.bom_id.product_qty
                            labour.actual_quantity = (bom_labour.product_qty * order.product_qty) / order.bom_id.product_qty
                    
                for bom_overhead in order.bom_id.overhead_cost_byproduct_ids:
                    overhead_id = order.overhead_cost_byproduct_ids.filtered(lambda overhead: overhead.product_id == bom_overhead.product_id)
                    if overhead_id:
                        for overhead in overhead_id:
                            overhead.product_qty = (bom_overhead.product_qty * order.product_qty) / order.bom_id.product_qty
                            overhead.actual_quantity = (bom_overhead.product_qty * order.product_qty) / order.bom_id.product_qty
        return rec

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
