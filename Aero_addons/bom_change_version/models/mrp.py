# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class MRPBom(models.Model):
    _inherit = 'mrp.bom'
    
    custom_version = fields.Float(
        string='Current Version',
        default=1.0,
        copy=False,
        readonly=True
    )
    original_bom_id = fields.Many2one(
        'mrp.bom',
        string='Original BOM',
        copy=False,
        readonly=True
    )
    bom_change_ids = fields.One2many(
        'bom.change.version',
        'bom_id',
        'BOM Change Order'
    )
    bom_change_count = fields.Integer(
        string='BOM Change Count',
        compute='_compute_bom_change_version',
        store=True,
    )
    
    @api.depends('bom_change_ids')
    def _compute_bom_change_version(self):
        for rec in self:
            rec.bom_change_count = len(rec.bom_change_ids)
    
    
    # @api.multi
    def action_show_bom_change_order(self):
        bom_changes = self.mapped('bom_change_ids')
        action = self.env.ref('bom_change_version.bom_change_order_action').sudo().read()[0]
        if len(bom_changes) > 0:
            action['domain'] = [('id', 'in', bom_changes.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    # @api.multi
    def action_view_bom_changer_order(self):
        action = self.env.ref('bom_change_version.bom_change_action')
        result = action.sudo().read()[0]
        result['context'] = {'default_product_template_id': self.product_tmpl_id.id, 
                             'default_product_id': self.product_id.id,
                             'default_bom_id':self.id}
        res = self.env.ref('bom_change_version.bom_change_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result
    
   