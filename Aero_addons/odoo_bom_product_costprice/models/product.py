# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.product'
    
    custom_bom_id = fields.Many2one(
        'mrp.bom',
        string='Bill of Material',
        copy=True,
    )
    custom_bom_cost_price = fields.Float(
        'Cost Price(As Per BOM)',
        compute='_compute_bom_costprice',
        store=True,
    )
    
    @api.depends(
        'bom_ids',
        'bom_ids.custom_price_subtotal',
        'custom_bom_id',
    )
    def _compute_bom_costprice(self):
        for rec in self:
             if rec.custom_bom_id:
                rec.custom_bom_cost_price = rec.custom_bom_id.custom_price_subtotal
             elif rec.bom_ids:
                bom =rec.bom_ids.sorted(reverse=True)[0]
                rec.custom_bom_cost_price = bom.custom_price_subtotal


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    custom_bom_id = fields.Many2one(
        'mrp.bom',
        string='Bill of Material',
        copy=True,
    )
    custom_bom_cost_price = fields.Float(
        'Cost Price(As Per BOM)',
        compute='_compute_bom_costprice',
        store=True,
    )
    
    @api.depends(
        'bom_ids',
        'bom_ids.custom_price_subtotal',
        'custom_bom_id',
    )
    def _compute_bom_costprice(self):
        for rec in self:
            if rec.custom_bom_id:
                rec.custom_bom_cost_price = rec.custom_bom_id.custom_price_subtotal
            elif rec.bom_ids:
                bom =rec.bom_ids.sorted(reverse=True)[0]
                rec.custom_bom_cost_price = bom.custom_price_subtotal
                    
