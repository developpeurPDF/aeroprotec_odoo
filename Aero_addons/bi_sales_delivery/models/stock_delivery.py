# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api
from datetime import datetime


class StockDeliveryInherit(models.Model):
    _inherit = "stock.move"

    delivery_date = fields.Datetime(string="Delivery Date")

    
    dict_date={}

    def _assign_picking(self):
        
        model_obj = self.env['ir.model'].sudo().search([('model','=','mrp.production')])
        if model_obj:
            mrp_production_list = []
            mrp_production = self.env['mrp.production'].sudo().search([])
            for proction in mrp_production:
                mrp_production_list.append(proction.name)
            # for move in self:
            #     if move.origin in mrp_production_list:
            #         return super(StockDeliveryInherit, self)._assign_picking()

        Picking = self.env['stock.picking']
        for move in self:
            if move.delivery_date:
                if self.company_id.allow_delivery_date == True : 
                    if move.delivery_date not in self.dict_date:
                        self.dict_date.update({
                            move.delivery_date.date():{
                                move.product_id,
                                move.name,
                                move.product_uom_qty,
                                move.reserved_availability,
                                move.quantity_done
                            }
                        })
                    else:
                        self.dict_date[move.delivery_date.date()].update({
                            move.product_id,
                            move.name,
                            move.product_uom_qty,
                            move.reserved_availability,
                            move.quantity_done
                        })
            else:
                move.delivery_date = move.date
            
            picking = False
            recompute = False
            picking = Picking.search([              
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('sc_date','=',move.delivery_date.date()),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], 
                limit=1)

            if picking:
                if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())

            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)

            if recompute:
                move.recompute
        
        return True

    def _get_new_picking_values(self):
        res = super(StockDeliveryInherit,self)._get_new_picking_values()
        if self.company_id.allow_delivery_date == True : 
            for move in self:
                if move.delivery_date:
                    res.update({
                        'scheduled_date' : move.delivery_date,
                        'sc_date':move.delivery_date.date()
                        })
                else:
                    res.update({
                        'scheduled_date' : fields.Datetime.now(),
                        'sc_date':move.delivery_date.date()
                        })
                

        return res


    def _prepare_procurement_values(self):
        self.ensure_one()
        group_id = self.group_id or False
        if self.rule_id:
            if self.rule_id.group_propagation_option == 'fixed' and self.rule_id.group_id:
                group_id = self.rule_id.group_id
            elif self.rule_id.group_propagation_option == 'none':
                group_id = False
        product_id = self.product_id.with_context(lang=self._get_lang())
        return {
            'product_description_variants': self.description_picking and self.description_picking.replace(product_id._get_description(self.picking_type_id), ''),
            'date_planned': self.date,
            'sale_line_id': self.sale_line_id.id,
            'date_deadline': self.date_deadline,
            'move_dest_ids': self,
            'group_id': group_id,
            'route_ids': self.route_ids,
            'warehouse_id': self.warehouse_id or self.picking_type_id.warehouse_id,
            'priority': self.priority,
            'orderpoint_id': self.orderpoint_id,
            'product_packaging_id': self.product_packaging_id,
        }
        

          
class InStockPicking(models.Model):
    _inherit="stock.picking"


    sc_date = fields.Date(string="Delivery Date")
    is_delivery_date = fields.Boolean(related='company_id.allow_delivery_date',string="Check Delivery Date")


    @api.depends('move_ids.delivery_date')
    def _compute_scheduled_date(self):
        for picking in self:
            if picking.is_delivery_date == True:
                for i in picking.move_ids:
                    if i.delivery_date == False:
                        picking.scheduled_date = fields.Datetime.now()
                    else:
                        picking.scheduled_date = str(min(i.mapped('delivery_date')))
            else:
                moves_dates = picking.move_ids.filtered(lambda move: move.state not in ('done', 'cancel')).mapped('date')
                if picking.move_type == 'direct':
                    picking.scheduled_date = min(moves_dates, default=picking.scheduled_date or fields.Datetime.now())
                else:
                    picking.scheduled_date = max(moves_dates, default=picking.scheduled_date or fields.Datetime.now())

