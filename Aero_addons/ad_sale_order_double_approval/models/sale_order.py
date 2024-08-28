# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api
import datetime

class ResCompany(models.Model):
    _inherit = 'res.company'

    double_approval = fields.Boolean(string="Double Approval",default=True)
    double_approval_type = fields.Selection([('individual','Individual'),('global','Global')],default='global',string="Double Approval Type")
    double_approval_amount = fields.Float(string="Double Approval Maximum Amount")
    double_email_alerts_approve = fields.Selection([('no_alerts','No Alerts'),('all_approval','To All Approval (Who have approval limit more than total amount of order)'),('by_team','By Team (Sales Channels)'),('specific_users','Specific User')],
            default='all_approval',string="Email Alert For Approval Orders")
    double_email_specific_user_id = fields.Many2one("res.users","Email Alert User")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    double_approval = fields.Boolean(string="Double Approval",related="company_id.double_approval",readonly=False)
    double_approval_type = fields.Selection([('individual','Individual'),('global','Global')],default='global',related="company_id.double_approval_type",string="Double Approval Type" ,readonly=False)
    double_approval_amount = fields.Float(string="Double Approval Maximum Amount",related="company_id.double_approval_amount",help="This amount will be consider when approval type is global." ,readonly=False)
    
    double_email_alerts_approve = fields.Selection([('no_alerts','No Alerts'),('all_approval','To All Approval (Who have approval limit more than total amount of order)'),('by_team','By Team (Sales Channels)'),('specific_users','Specific User')],
            default='all_approval',related="company_id.double_email_alerts_approve",string="Email Alert For Approval Orders",readonly=False)
    double_email_specific_user_id = fields.Many2one("res.users","Email Alert User",related="company_id.double_email_specific_user_id",readonly=False)
    
class ResUser(models.Model):
    _inherit = 'res.users'
    
    double_max_limit = fields.Float("Maximum Sales Limit(For Sales User)",help="This amount will be consider when approval type is individual and user not given 'Sales Order Double Approval' group.")
    double_approval_limit = fields.Float("Maximum Sales Approval Limit (For Approver)",help="This amount will be consider when approval type is individual and user(sales manager) has given 'Sales Order Double Approval' group.")
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    hide_approve_btn = fields.Boolean("Hide Approve button",compute="hide_approve_btn_conditionally",default = True)
    state = fields.Selection(selection_add=[('draft','Quotation'),('sent','Quotation Sent'),('approve','à Approuver'),('approve2','Approuvé'),('refuse','Refused'),('sale','Sales Order'),('done','Locked'),('cancel','Cancelled'),],
                               string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    so_refuse_reason_id = fields.Many2one("sh.so.refuse.reason",string= "Sale Order Refuse Reason",help="This field display reason of quatation cancellation")
    
    sh_approve_by = fields.Many2one("res.users",string="Approué par", copy=False, index=True, track_visibility='onchange')
    sh_approve_time = fields.Datetime(string="approuvé le", copy=False, index=True, track_visibility='onchange')
    sh_refuse_by = fields.Many2one("res.users",string="Réfuser par", copy=False, index=True, track_visibility='onchange')
    sh_refuse_reason = fields.Text(string="Raison de refus", copy=False, index=True, track_visibility='onchange')
    sh_refuse_time = fields.Datetime(string="refuser le", copy=False, index=True, track_visibility='onchange')
    
    
    @api.depends('state')
    def hide_approve_btn_conditionally(self):
        if self.user_has_groups('ad_sale_order_double_approval.sh_group_sale_order_double_approval') and self.state =='approve': # If Double Approval Permission   
                self.hide_approve_btn =  False

        else:    
            self.hide_approve_btn =  True
            
    def action_approve(self):
        if self:
            for data in self:
                sale_obj = data.env['sale.order'].search([('id','=',data.id)])
                sale_obj.write({
                        'sh_approve_by': data.env.user.id,
                        'sh_approve_time': datetime.datetime.now()
                })
                data.state = 'approve2'
        
    
    def action_refuse(self,context=None):
        return {
        'name': ('ajouter une riason'),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'refuse.reason.wizard',
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target':'new'
        }            
    def _make_url(self, record_id, model_name, menu_id, action_id):
        ir_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_param.get_param('web.base.url')
        if base_url:
            base_url += \
                '/web?#id=%s&action=%s&model=%s&view_type=form&menu_id=%s' \
                % (record_id, action_id, model_name, menu_id)
        return base_url
    def send_email_alert_noritification(self):
        
            send_email_to  = ''
            users_ids = []
            template = self.env.ref('ad_sale_order_double_approval.ad_sale_order_double_approval_mail_template')
                            
            grp_id = self.env.ref('ad_sale_order_double_approval.sh_group_sale_order_double_approval').id
               
            if grp_id :
                res_grps = self.env['res.groups'].search([('id','=',grp_id)],limit=1)                
                users_ids = self.env['res.users'].search([('groups_id', '=', grp_id)])
                menu_id = self.env.ref('sale.menu_sale_quotations').id
                action_id = self.env.ref('sale.action_quotations_with_onboarding').id
                so_url = self._make_url(self.id, self._name, menu_id, action_id)                        
                for au_user in users_ids:
                 email_body = ''' <span style='font-style: 16px;font-weight:
                  bold;'>Cher, %s</span>''' % (au_user.name) + ''' <br/><br/>
                  ''' + ''' <span style='font-style: 14px;'> un devis de 
                  <span style='font-weight: bold;'>%s</span> en attente de votre approbation,</span>''' % \
                       (self.env.user.name) + ''' <br/>''' + '''<span
                       style='font-style: 14px;'>Veuillez y accéder à partir du bouton ci-dessous</span> <div style="margin-top:40px;"> <a
                       href="''' + so_url + '''" style="background-color:
                       #1abc9c; padding: 20px; text-decoration: none; color:
                        #fff; border-radius: 5px; font-size: 16px;"
                        class="o_default_snippet_text">Voir Devis</a></div>
                        <br/><br/>'''
                 email_id = self.env['mail.mail'].\
                    sudo().create({'subject': 'DEVIS en attente de votre approbation',
                            'email_from': self.env.user.partner_id.email,
                            'email_to': au_user.partner_id.email,
                            'message_type': 'email',
                            'model':'sale.order',
                            'res_id': self.id,
                            'body_html': email_body
                            })
                 email_id.send()    
#             if template and users_ids:           
#                     res_users = self.env['res.users'].search([('id','in',users_ids)]) 
                                            
#                     if res_users:                                         
#                         for record in res_users:
#                             if record.email:
#                                 mail_res = template.send_mail(self.id,force_send=True,email_values={'email_to':record.email})          
        
        
    def demande_approuve(self): # overwrite existing
        
        if self.env.user.company_id.double_approval:
        
            dbl_apr_tp = self.env.user.company_id.double_approval_type 
            
            if dbl_apr_tp == 'global':   # Company wise
                glb_dbl_apr_amt = self.env.user.company_id.double_approval_amount 
                   
#                 if self.user_has_groups('ad_sale_order_double_approval.sh_group_sale_order_double_approval'):  #  If Double Approval Permission
#                     ind_dbl_aprl_limit = self.env.user.double_approval_limit 
#                     self.hide_approve_btn = True
#                     res = super(SaleOrder,self).action_confirm()
#                     return res            
                   
#                 else: 
                if self.state != 'approve':   # Executes if not already on approve stage 
                            self.send_email_alert_noritification()
                            self.state = 'approve'
            return False
    def action_draft(self):
        res = super(SaleOrder,self).action_draft()
        return res     
