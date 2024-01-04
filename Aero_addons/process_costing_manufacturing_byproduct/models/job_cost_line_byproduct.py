# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BomJobCostLine(models.Model): 
    _name = 'bom.job.cost.line.byproduct'
    _description = 'Bom Job Cost Line ByProduct'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price')
    def _compute_total_cost_byproduct(self):
        for rec in self:
            rec.total_cost = rec.product_qty * rec.cost_price

    @api.depends('actual_quantity','cost_price')
    def _compute_actual_total_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_quantity * rec.cost_price

    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',#product.uom
        string='UOM',
        required=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute="_compute_total_cost_byproduct",
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        related='bom_byproduct_id.custom_currency_id',
        string='Currency',
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
        required=False,
    )
    bom_byproduct_id = fields.Many2one(
        'mrp.bom',
        string="BOM",
    )
    actual_quantity = fields.Float(
        string='Actual Qty',
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost Price',
#         compute="_compute_actual_mrp_total_cost",
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.cost_price = rec.product_id.lst_price
            rec.uom_id = rec.product_id.uom_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
