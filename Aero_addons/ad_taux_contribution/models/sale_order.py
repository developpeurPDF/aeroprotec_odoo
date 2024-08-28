from odoo import api, fields, models
from datetime import datetime, date, timedelta

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    guarantee_percentage_amount = fields.Float(compute='compute_guarantee_percentage_amount')
    guarantee_return = fields.Boolean(string="Contribution énergétique", related='partner_id.contribution_enrg', store=True)
    rg_percentage = fields.Float('Taux de Contribution énergétique', related='partner_id.company_id.ad_montant_rg', store=True)

    prime_total_amount = fields.Float(compute='compute_prime_percentage')
    prime = fields.Boolean(string="Contribution environnementale", related='partner_id.contribution_env', store=True)
    prime_amount = fields.Float("Taux de Contribution environnementale", related='partner_id.company_id.ad_montant_cee', store=True)



    def _prepare_invoice(self):
        res = super()._prepare_invoice()

        if self.guarantee_return and self.env.context.get('retenue_de_garantie'):
            res.update({
                'guarantee_return': self.guarantee_return,
                'rg_percentage': self.rg_percentage,
            })
        return res

    @api.depends('amount_untaxed', 'amount_tax', 'rg_percentage')
    def compute_guarantee_percentage_amount(self):
        for rec in self:
            try:
                tth = rec.amount_untaxed
                # print("TTH (Hors taxe)", tth)
                # tva = rec.amount_tax/2
                # print("TVA (Tax)", tva)
                rec.guarantee_percentage_amount = tth * (rec.rg_percentage / 100)
                print("Montant de la garantie", rec.guarantee_percentage_amount)
            except Exception as e:
                print("Erreur dans compute_guarantee_percentage_amount: ", e)
                rec.guarantee_percentage_amount = 0

    @api.depends('amount_total')
    def compute_prime_percentage(self):
        for rec in self:
            try:
                tth = rec.amount_untaxed
                rec.prime_total_amount = tth * (rec.prime_amount / 100)
                print("Montant de la prime", rec.prime_total_amount)
            except Exception as e:
                print("Erreur dans compute_guarantee_percentage_amount: ", e)
                rec.prime_total_amount = 0


    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'amount_tax',
                 'currency_id', 'rg_percentage', 'guarantee_return', 'guarantee_percentage_amount', 'prime', 'prime_amount')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

            # Initial total amount (TTH + TVA)
            tth = order.amount_untaxed
            tva = order.amount_tax
            prime_amount = order.prime_total_amount if order.prime else 0
            guarantee_amount = order.guarantee_percentage_amount if order.guarantee_return else 0
            # print("guarantee_amount",guarantee_amount)

            # Total amount with TTH + TVA + Prime + Guarantee
            ttc_with_modifications = tth + (tva/2) + prime_amount + guarantee_amount

            # Formatting the total amount
            formatted_amount_total = '{:.2f}'.format(ttc_with_modifications).replace('.', ',') + ' ' + str(order.currency_id.symbol)

            # Update tax totals dictionary
            tax_totals['formatted_amount_total'] = formatted_amount_total
            # print("tax_totals['formatted_amount_total']", tax_totals['formatted_amount_total'])
            tax_totals['amount_total'] = ttc_with_modifications
            # print("tax_totals['amount_total']", tax_totals['amount_total'])

            if order.prime:
                tax_totals['prime_amount'] = prime_amount
                tax_totals['prime_amount_formatted'] = '{:.2f}'.format(prime_amount).replace('.', ',') + ' ' + str(order.currency_id.symbol)
                # print("tax_totals['prime_amount_formatted']", tax_totals['prime_amount_formatted'])

            if order.guarantee_return:
                tax_totals['guarantee_amount'] = guarantee_amount
                tax_totals['guarantee_percentage_amount_formatted'] = '{:.2f}'.format(guarantee_amount).replace('.', ',') + ' ' + str(order.currency_id.symbol)
                # tax_totals['rg_percentage'] = order.rg_percentage
                # print("tax_totals['guarantee_percentage_amount_formatted']", tax_totals['guarantee_percentage_amount_formatted'])

            # Assign the formatted amount total to tax_totals
            tax_totals['custom'] = tax_totals['formatted_amount_total']
            order.tax_totals = tax_totals
            # print("order.tax_totals",order.tax_totals)