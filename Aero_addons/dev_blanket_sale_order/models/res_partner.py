# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date
from odoo.exceptions import ValidationError


class res_partner(models.Model):
    _inherit = "res.partner"

    def action_view_balnket_order(self):
        action = self.env.ref('dev_blanket_sale_order.action_Blanket_orders').read()[0]
        balnket_order = self.env['sale.order'].search([('partner_id','=',self.id),('order_type','=','blanket')])
        if not balnket_order:
            raise ValidationError(_("No Balnket Order"))
        if len(balnket_order) > 1:
            action['domain'] = [('id', 'in', balnket_order.ids)]
        elif balnket_order:
            action['views'] = [(self.env.ref('dev_blanket_sale_order.form_dev_blanket_sale_order').id, 'form')]
            action['res_id'] = balnket_order.id
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
