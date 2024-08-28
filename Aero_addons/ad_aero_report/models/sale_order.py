from odoo import api, fields, models, _
from datetime import datetime, timedelta, time
from pytz import timezone, utc

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_formatted_date(self):
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        today = datetime.today()
        day_name = days[today.weekday()]
        day = today.day
        month_name = months[today.month - 1]
        year = today.year
        return f'Le {day_name} {day} {month_name} {year}'


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # def get_frais_amount(self):
    #     self.ensure_one()
    #     frais_amount = 0.0
    #     for tax in self.tax_id.filtered(lambda t: t.frais):
    #         tax_amount = \
    #         tax.compute_all(self.price_unit, self.order_id.currency_id, self.product_uom_qty, product=self.product_id,
    #                         partner=self.order_id.partner_shipping_id)['taxes'][0]['amount']
    #         frais_amount += tax_amount
    #     return frais_amount

    def get_frais_details(self):
        self.ensure_one()
        frais_details = []
        for tax in self.tax_id.filtered(lambda t: t.frais):
            tax_amount = \
            tax.compute_all(self.price_unit, self.order_id.currency_id, self.product_uom_qty, product=self.product_id,
                            partner=self.order_id.partner_shipping_id)['taxes'][0]['amount']
            frais_details.append({
                'description': tax.description or tax.name,
                'amount': tax_amount,
            })
        return frais_details