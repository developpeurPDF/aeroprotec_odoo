# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

class wiz_mass_sale_order(models.TransientModel):
    _name = 'wiz.mass.sale.order'
    _description = "Mass Sale Order Wizard"
    
     
    def mass_sale_order_email_send(self):
        context = self._context
        active_ids = context.get('active_ids')
        super_user = self.env['res.users'].browse(SUPERUSER_ID)
        for a_id in active_ids:
            sale_order_brw = self.env['sale.order'].sudo().browse(a_id)
            for partner in sale_order_brw.partner_id:
                partner_email = partner.email
                if not partner_email:
                    raise UserError(_('%s customer has no email id please enter email address')
                            % (sale_order_brw.partner_id.name)) 
                else:
                    template_id = sale_order_brw._find_mail_template()
                    # template_id = self.env['mail.template'].browse(template)

                    email_values = {}
                    for template_data in template_id:
                        email_values['body_html'] = template_data.id
                    email_values['email_to'] = partner.email
                    if template_id:
                        values = template_id.generate_email(a_id, fields=email_values)
                        email_values['res_id'] = False
                        email_values['body_html'] = values.get('body_html') or ''
                        email_values['subject'] = values.get('subject') or 'Quotation (' + sale_order_brw.name + ')'
                        email_values['author_id'] = self.env['res.users'].browse(request.env.uid).partner_id.id
                        
                        vals = {
                            'name' : sale_order_brw.name,
                            'type' : 'binary',
                            'datas' : values['attachments'][0][1],
                            'res_id' : a_id,
                            'res_model' : 'sale.order',                            
                        }
                        attachment_id = self.env['ir.attachment'].sudo().create(vals)
                        email_values['attachment_ids'] = [(6,0,[attachment_id.id])]
                        msg_id = self.env['mail.mail'].sudo().create(email_values)
                        sale_order_brw.write({'is_sale_order_sent' : True})

                        if msg_id:
                            self.env['mail.mail'].sudo().send([msg_id])

        return True

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    is_sale_order_sent = fields.Boolean('Is Order Sent',default=False)

    def copy(self, default=None):
        res = super(SaleOrder,self).copy(default)
        res.update({'is_sale_order_sent': False})
        return res
    
class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    
    def send_mail(self, auto_commit=False):
        context = self._context
        if context.get('default_model') == 'sale.order' and \
                context.get('default_res_id') and context.get('mark_so_as_sent'):
            order = self.env['sale.order'].sudo().browse(context['default_res_id'])
            # Set boolean field true after mass sale order email sent
            order.write({
                'is_sale_order_sent' : True
            })
            order = order.with_context(mail_post_autofollow=True)
            #order.sent = True
            order.message_post(body=_("Sale Order sent"))
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
                    
        
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
