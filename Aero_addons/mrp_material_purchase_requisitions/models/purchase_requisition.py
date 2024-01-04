# -*- coding: utf-8 -*-

from odoo import models, fields

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'
    
    custom_mo_mrp_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        readonly=True,
    )
    custom_mo_workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Work Order',
        readonly=True,
    )
    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
