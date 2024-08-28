# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import re
import time
from datetime import datetime
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    sale_history_ids = fields.One2many('sale.order.line.history', 'order_id', 'History Lines', readonly=True)        

class sale_order_line(models.Model):
        _inherit = 'sale.order.line'
        

        @api.model_create_multi
        def create(self, vals_list):
            res = super(sale_order_line, self).create(vals_list)
            history_obj = self.env['sale.order.line.history']
            for rec in res:
                code_line = {
                    'product_id': rec.product_id.id,
                    'product_qty': rec.product_uom_qty,
                    'product_uom': rec.product_uom.id,
                    'price_unit' : rec.price_unit,
                    'price_unit_old': 0.0,
                    'order_id': rec.order_id.id,
                    'line_id': rec.id,
                } 
                history_obj.create(code_line)
        
            return res

        
        def write(self, vals):
            sale_line_history_obj=self.env['sale.order.line.history']
            result = super(sale_order_line, self).write(vals)
            history_ids = sale_line_history_obj.search([])
            if vals.get('price_unit'):
                for line in self:
                    for history in history_ids:
                        if  history.product_id == line.product_id:
                            history.write({'price_unit': line.price_unit,'price_unit_old': history.price_unit})
                return result

class prepurchase_order_line_history(models.Model):
        _name = 'sale.order.line.history'
        _description = 'Sale Order Line History'

        product_id = fields.Many2one('product.product', 'Product', domain=[('purchase_ok','=',True)], change_default=True)
        product_qty = fields.Float('Quantity', required=True, default=1.0)
        product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure')
        price_unit = fields.Float('New Price', required=True)
        price_unit_old = fields.Float('Old Price', required=True)
        taxes_id = fields.Many2many('account.tax', 'purchase_order_taxe', 'ord_id', 'tax_id', 'Taxes')
        order_id = fields.Many2one('sale.order', 'Order Reference', required=True, ondelete='cascade')
        company_id = fields.Many2one(related='order_id.company_id',string='Company', readonly=True)
        partner_id = fields.Many2one(related='order_id.partner_id',string='Partner',readonly=True)
        state = fields.Selection([('draft', 'Draft')], 'Status', readonly=True,default='draft',
                                                                    help=' * The \'Draft\' status is set automatically when purchase order in draft status.')
        line_id = fields.Many2one('sale.order.line', 'Sale Order line')
        



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
