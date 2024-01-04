# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    custom_mo_material_requisition_count = fields.Integer(
        compute='_compute_requistions_count', 
        string='Material Requisitions Count'
    )
    custom_mo_material_requisition_ids = fields.One2many(
        'material.purchase.requisition',
        'custom_mo_mrp_id',
        string='Material Requisitions'
    )
    
    # @api.multi #odoo13
    @api.depends('custom_mo_material_requisition_ids')
    def _compute_requistions_count(self):
        for rec in self:
            rec.custom_mo_material_requisition_count = len(rec.custom_mo_material_requisition_ids)
            
    # @api.multi #odoo13
    def action_see_material_requisitions(self):
        self.ensure_one()
        action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition').sudo().read()[0]
        action['domain'] = [('custom_mo_mrp_id', '=', self.id)]
        return action