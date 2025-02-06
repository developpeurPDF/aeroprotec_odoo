# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SalesDeliveryInherit(models.Model):
    _inherit = "mrp.production"

    delivery_date = fields.Datetime(string="Date de fin de traitement", compute='_compute_delivery_date')

    @api.depends('product_id.days_to_prepare_mo', 'date_planned_start')
    def _compute_delivery_date(self):
        for record in self:
            final_date = False

            # Vérifiez d'abord s'il y a une date_recale mentionnée dans les lignes de commande
            if record.sale_order_ids and record.sale_order_ids.order_line:
                for line in record.sale_order_ids.order_line:
                    if line.date_recale:
                        final_date = line.date_recale
                    elif line.date_livraison:
                        final_date = line.date_livraison
                        break

            # Si aucune date_recale n'est trouvée, appliquez le calcul habituel
            if not final_date and record.date_planned_start and record.product_id.days_to_prepare_mo:
                final_date = self.env['sale.order.line']._calculate_final_date(
                    record.date_planned_start,
                    (record.product_id.days_to_prepare_mo + record.product_id.produce_delay
                     if record.product_id.sale_delay == 0
                     else record.product_id.sale_delay + record.product_id.produce_delay)
                )

            # Vérifiez si la date finale est définie
            if final_date:
                record.delivery_date = final_date
            else:
                # Assigner la date de début planifiée comme fallback
                record.delivery_date = record.date_planned_start




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
