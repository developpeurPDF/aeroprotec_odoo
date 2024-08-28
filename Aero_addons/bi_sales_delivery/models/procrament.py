# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api


class ProcurementInherit(models.Model):
    _inherit = "stock.rule"
    
    delivery_date = fields.Datetime(string="Delivery Date")

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        
        result = super(ProcurementInherit, self)._get_stock_move_values(\
            product_id, product_qty, product_uom, location_id, name, origin, company_id, values)

        if values.get('delivery_date'):
            result.update({
                'delivery_date' : values.get('delivery_date')

                })
        else:
            if values.get('sale_line_id'):
                delivery_date = self.env['sale.order.line'].search([('id','=',values.get('sale_line_id'))],limit=1).delivery_dates
                result.update({
                    'delivery_date' : delivery_date
                    })
            else:
                result.update({
                    'delivery_date' : values.get('delivery_date')
                    })
                print('Delivery Date:', result.get('delivery_date'))


        return result

        