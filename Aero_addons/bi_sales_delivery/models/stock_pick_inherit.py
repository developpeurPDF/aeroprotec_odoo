# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import UserError


class SalesInherit(models.Model):
    _inherit = "stock.picking"
    
    def action_assign(self):
        res = super(SalesInherit, self).action_assign()
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_ids').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if moves:
            if self.is_delivery_date == True : 
               res = super(SalesInherit, self).action_assign()
        else:
            raise UserError(_('Nothing to check the availability for.'))
        moves._action_assign()


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, bom):
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_dest_id, name, origin,
                                                      company_id, values, bom)
        if values.get('move_dest_ids'):
            move_dest_ids = values.get('move_dest_ids')[0]
            for move in move_dest_ids:
                if move.sale_line_id:
                    res.update({
                        'sale_line_id': move.sale_line_id.id
                    })

        return res