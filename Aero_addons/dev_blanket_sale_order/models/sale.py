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
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        res =  super(SaleOrder, self)._onchange_partner_id_warning()
        balnket_order_ids = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),('order_type','=','blanket')])
        if self.partner_id and self.order_type == 'blanket' and balnket_order_ids:
            msg= "Blanket order allready created"
            return { 'warning': {'title': 'Blanket Order Created', 'message':msg } }
        return res

    def create_sale_quotation(self):
        if not self.order_line:
            raise ValidationError(_('''Please add some Order Lines'''))
        data = []
        for line in self.order_line:
            data.append((0, 0, {'sale_line_id': line.id}))
        if data:
            create_quote_id = self.env['create.sale.quotation'].create({'line_ids': data})
            if create_quote_id:
                action = self.env.ref('dev_blanket_sale_order.action_create_sale_quotation').read()[0]
                action.update({'res_id': create_quote_id.id})
                return action

    @api.model
    def create(self, vals):
        if self._context.get('default_order_type') == 'blanket':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.blanket') or '/'
        return super().create(vals)

    def open_blanket_order(self):
        self.blanket_state = 'open'

    def cancel_blanket_order(self):
        self.blanket_state = 'cancelled'

    def set_to_new_blanket_order(self):
        self.blanket_state = 'draft'

    def compute_sale_quote_count(self):
        for rec in self:
            rec.sale_quote_count = len(rec.blanket_order_ids)

    def view_sale_quotations(self):
        orders = self.mapped('blanket_order_ids')
        action = self.env.ref('sale.action_orders').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def expire_blanket_orders(self):
        blanket_ids = self.env['sale.order'].search([('blanket_expiry_date', '=', date.today()),
                                                     ('order_type', '=', 'blanket')])
        if blanket_ids:
            for blanket_id in blanket_ids:
                blanket_id.blanket_state = 'expired'

    blanket_state = fields.Selection(selection=[('draft', 'New'),
                                                ('open', 'Open'),
                                                ('expired', 'Expired'),
                                                ('cancelled', 'Cancelled')], string='Blanket State', default='draft', copy=False, tracking=True)
    order_type = fields.Selection(selection=[('sale', 'Sale'), ('blanket', 'Blanket')], string='Type of Order')
    blanket_expiry_date = fields.Date(string='Expiry Date')
    blanket_order_ids = fields.Many2many(comodel_name='sale.order', relation='sale', column1='order_type', column2='blanket_expiry_date', string='Blanket Quotation')
    sale_quote_count = fields.Integer(string='Sale Orders', compute='compute_sale_quote_count')

    # @api.depends('order_line.tax_id', 'order_line.price_unit', 'order_line.frais_amount', 'amount_total',
    #              'amount_untaxed', 'currency_id')
    # def _compute_tax_totals(self):
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type)
    #         tax_base_lines = []
    #         for line in order_lines:
    #             tax_base_line = line._convert_to_tax_base_line_dict()
    #             if self.appliquer_seuil_a_la_ligne:
    #                 tax_base_line[
    #                     'price_unit'] = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else line.price_subtotal
    #                 tax_base_lines.append(tax_base_line)
    #             else:
    #                 tax_base_line[
    #                     'price_unit'] += line.frais_amount / line.product_uom_qty if line.product_uom_qty else line.frais_amount
    #                 tax_base_lines.append(tax_base_line)
    #         order.tax_totals = self.env['account.tax']._prepare_tax_totals(
    #             tax_base_lines,
    #             order.currency_id or order.company_id.currency_id,
    #         )



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def compute_remaining_qty(self):
        for record in self:
            record.remaining_qty = record.product_uom_qty - record.consumed_qty

    remaining_qty = fields.Float(string='Quantité restante', compute='compute_remaining_qty')
    consumed_qty = fields.Float(string='Consumed Quantity')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
