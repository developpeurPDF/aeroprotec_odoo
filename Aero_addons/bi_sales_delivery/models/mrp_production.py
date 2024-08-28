# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api
from datetime import timedelta, datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one('sale.order.line',string="Sale Order Line")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MrpProduction, self).create(vals_list)
        if res.company_id.allow_delivery_date == True :
            for r in res:
                stock_move = res.procurement_group_id.mrp_production_ids.move_dest_ids.filtered(lambda x:x.product_id.id == r.product_id.id)
                for move in stock_move :
                    if move.sale_line_id == r.sale_line_id :

                        if res.company_id.manufacturing_lead and r.product_id.produce_delay and res.company_id.security_lead and r.product_id.sale_delay:
                            sale_days = r.product_id.sale_delay
                            security_days = res.company_id.security_lead
                            delay_days =  r.product_id.produce_delay
                            manufacturing_days = res.company_id.manufacturing_lead
                            count_days = sale_days - security_days -manufacturing_days - delay_days
                            final_date = r.sale_line_id.delivery_dates - timedelta(days=count_days or 0.0)

                        elif res.company_id.manufacturing_lead and r.product_id.produce_delay and res.company_id.security_lead:
                            manufacturing_days = res.company_id.manufacturing_lead
                            delay_days =  r.product_id.produce_delay
                            security_days = res.company_id.security_lead
                            count_days =manufacturing_days + delay_days +security_days
                            final_date = r.sale_line_id.delivery_dates - timedelta(days=count_days or 0.0)

                        elif res.company_id.manufacturing_lead and r.product_id.produce_delay and r.product_id.sale_delay:
                            manufacturing_days = res.company_id.manufacturing_lead
                            delay_days =  r.product_id.produce_delay
                            security_days = r.product_id.sale_delay
                            count_days =delay_days - manufacturing_days
                            if move.delivery_date:
                                final_date = move.delivery_date - timedelta(days=count_days or 0.0)
                            else:
                                final_date = move.date - timedelta(days=count_days or 0.0)
                        
                        elif res.company_id.manufacturing_lead and r.product_id.produce_delay:
                            security_days = res.company_id.manufacturing_lead
                            delay_days =  r.product_id.produce_delay
                            count_days =  delay_days +security_days
                            if move.delivery_date:
                                final_date = move.delivery_date - timedelta(days=count_days or 0.0)
                            else:
                                final_date = move.date - timedelta(days=count_days or 0.0)
                        
                        elif res.company_id.manufacturing_lead:
                            delay_days = res.company_id.manufacturing_lead
                            final_date = move.delivery_date - timedelta(days=delay_days or 0.0)
                        elif r.product_id.produce_delay:
                            delay_days =  r.product_id.produce_delay
                            if move.delivery_date:
                                final_date = move.delivery_date - timedelta(days=delay_days or 0.0)
                            else:
                                 final_date = move.date - timedelta(days=delay_days or 0.0)
                        else:
                            if move.delivery_date:
                                final_date = move.delivery_date 
                            else:
                                final_date = move.date 

                        r.date_planned_start = final_date or datetime.now()
        return res

            
         
