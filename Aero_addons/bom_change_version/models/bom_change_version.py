# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BomChangeRequestVersion(models.Model):
    _name = 'bom.change.version'
    _deacription = "BOM Change Order Version"
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(
        string='Name',
        copy=False,
        readonly=True,
    )
    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product Variant',
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        required=True,
        string='Original BOM',
    )
    state = fields.Selection(
        [('draft','New'),
         ('process','Processed'),
         ('validate','Validated'),
         ('done','Activated BOM'),
         ('cancel','Cancelled')],
        string='State',
        default='draft',
        tracking=True,
        copy=False, 
    )
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.user.company_id, 
        string='Company', 
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users', 
        default=lambda self: self.env.user.id, 
        string='Responsible User', 
    )
    new_bom_id = fields.Many2one(
        'mrp.bom',
        string='New BOM',
        readonly=True,
        copy=False,
    )
    notes = fields.Text(
        string='Internal Notes',
        copy=True,
    )
    reason = fields.Text(
        string='Reason',
        copy=True,
    )
    current_version = fields.Float(
        related='bom_id.custom_version',
        string='Original BOM Version',
        store=True,
        copy=False,
        readonly=True,
    )
    new_bom_version = fields.Float(
        related='new_bom_id.custom_version',
        string='New BOM Version',
        store=True,
        copy=False,
        readonly=True,
    )
    change_date = fields.Date(
        string='Date',
        default=fields.date.today(),
        required=True,
        copy=False
    )
    processed_by_id = fields.Many2one(
        'res.users',
        string='Processed By',
        copy=False,
        readonly=True,
    )
    processed_date = fields.Datetime(
        string='Processed Date',
        copy=False,
        readonly=True,
    )
    validated_by_id = fields.Many2one(
        'res.users',
        string='Validated By',
        copy=False,
        readonly=True,
    )
    validated_date = fields.Datetime(
        string='Validated Date',
        copy=False,
        readonly=True,
    )
    activated_by_id = fields.Many2one(
        'res.users',
        string='Activated By',
        copy=False,
        readonly=True,
    )
    activated_date = fields.Datetime(
        string='Activated Date',
        copy=False,
        readonly=True,
    )
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bom.change.request') or 'New'
        return super(BomChangeRequestVersion, self).create(vals)
    
    # @api.multi
    def show_newbom_change_request(self):
        self.ensure_one()
        res = self.env.ref('mrp.mrp_bom_form_action')
        res = res.sudo().read()[0]
        res['domain'] = str([('id','=',self.new_bom_id.id)])
        return res
        
    
    # @api.multi
    def action_in_process(self):
        for rec in self:
            if rec.bom_id:
                bom_copy = rec.bom_id.copy()
                rec.new_bom_id = bom_copy.id
                rec.new_bom_id.custom_version = rec.current_version + 1
                rec.new_bom_id.original_bom_id = rec.bom_id.id
                rec.new_bom_id.active = False
                rec.state = 'process'
                rec.processed_by_id = self.env.user.id
                rec.processed_date = fields.Datetime.now()
            else:
                 raise UserError(_('Please Select the Original BOM.'))
    
    # @api.multi
    def action_validate(self):
        for rec in self:
            rec.state = 'validate'
            rec.validated_by_id = self.env.user.id
            rec.validated_date = fields.Datetime.now()
    
    # @api.multi
    def action_done(self):
        for rec in self:
            if rec.new_bom_id.active != True:
                rec.new_bom_id.active = True
                rec.bom_id.active = False
            rec.state = 'done'
            rec.activated_by_id = self.env.user.id
            rec.activated_date = fields.Datetime.now()
    
    # @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    
    # @api.multi
    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'
    
    # @api.multi
    def unlink(self):
        for bom_change in self:
            if bom_change.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete BOM Change Order is not draft or cancelled.'))
        return super(BomChangeRequestVersion, self).unlink()