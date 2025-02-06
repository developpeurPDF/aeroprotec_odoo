# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import timedelta, datetime

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    is_delivery_date = fields.Boolean(related='company_id.allow_delivery_date')


class SalesDeliveryInherit(models.Model):
    _inherit = "sale.order.line"

    delivery_dates = fields.Datetime(string="Date début trait.t", index=True,default=fields.Datetime.now,copy=False)


    def _prepare_procurement_values(self, group_id):
        res = super(SalesDeliveryInherit, self)._prepare_procurement_values(group_id=group_id)

        if self.company_id.allow_delivery_date:
            delay_days = self.product_id.sale_delay if self.product_id.sale_delay > 0 else self.product_id.produce_delay
            final_date = self._calculate_final_date(self.delivery_dates, delay_days)
            date_deadline = final_date
        else:
            final_date = self.delivery_dates
            date_deadline = self.delivery_dates

        res.update({
            'delivery_date': final_date,
            'date_deadline': date_deadline
        })

        return res

    def _calculate_final_date(self, start_date, delay_days):
        # Convertir start_date en datetime si ce n'est pas déjà le cas
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        current_date = start_date
        days_added = 0

        while days_added < delay_days:
            current_date += timedelta(days=1)
            if self._is_working_day(current_date):
                days_added += 1

        return current_date

    def _is_working_day(self, date):
        # Vérifier si le jour est un samedi ou un dimanche
        if date.weekday() >= 5:
            return False

        # Vérifier si la date est un jour férié
        public_holidays = self.env['resource.calendar.leaves'].search([
            ('date_from', '<=', date),
            ('date_to', '>=', date)
        ])
        if public_holidays:
            return False

        return True