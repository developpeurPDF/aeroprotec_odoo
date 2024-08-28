# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SalesDeliveryInherit(models.Model):
    _inherit = "mrp.production"

    delivery_date = fields.Datetime(string="Delivery Date")


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin,
                                                      company_id, values, bom)
        if values.get('move_dest_ids'):
            move_dest_ids = values.get('move_dest_ids')[0]
            for move in move_dest_ids:
                if move.delivery_date:
                    res.update({
                        'delivery_date': move.delivery_date
                    })

            return res
