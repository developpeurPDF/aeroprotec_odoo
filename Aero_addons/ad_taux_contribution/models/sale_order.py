from odoo import api, fields, models
from datetime import datetime, date, timedelta

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    energie_percentage_amount = fields.Float(compute='compute_energie_percentage_amount')
    energie_return = fields.Boolean(string="Contribution énergétique", related='partner_id.contribution_enrg')
    rg_percentage = fields.Float('Taux de Contribution énergétique', related='partner_id.company_id.ad_montant_rg')

    cont_env_total_amount = fields.Float(compute='compute_cont_env_percentage')
    cont_env = fields.Boolean(string="Contribution environnementale", related='partner_id.contribution_env')
    cont_env_amount = fields.Float("Taux de Contribution environnementale", related='partner_id.company_id.ad_montant_cee')



    def _prepare_invoice(self):
        res = super()._prepare_invoice()

        if self.energie_return and self.env.context.get('contribution_energie'):
            res.update({
                'energie_return': self.energie_return,
                'rg_percentage': self.rg_percentage,
            })
        res['rg_percentage'] = self.rg_percentage
        res['energie_return'] = self.energie_return
        res['cont_env'] = self.cont_env
        res['cont_env_amount'] = self.cont_env_amount

        return res

    @api.depends('amount_untaxed', 'amount_tax', 'rg_percentage')
    def compute_energie_percentage_amount(self):
        for rec in self:
            try:
                tth = rec.amount_untaxed
                # print("TTH (Hors taxe)", tth)
                # tva = rec.amount_tax/2
                # print("TVA (Tax)", tva)
                rec.energie_percentage_amount = tth * (rec.rg_percentage / 100)
                
            except Exception as e:
                
                rec.energie_percentage_amount = 0

    @api.depends('amount_total')
    def compute_cont_env_percentage(self):
        for rec in self:
            try:
                tth = rec.amount_untaxed
                rec.cont_env_total_amount = tth * (rec.cont_env_amount / 100)
                
            except Exception as e:
                
                rec.cont_env_total_amount = 0


    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'amount_tax',
                 'currency_id', 'rg_percentage', 'energie_return', 'energie_percentage_amount', 'cont_env', 'cont_env_amount')
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
            cont_env_amount = order.cont_env_total_amount if order.cont_env else 0
            energie_amount = order.energie_percentage_amount if order.energie_return else 0
            # print("energie_amount",energie_amount)

            # Total amount with TTH + TVA + cont_env + energie
            ttc_with_modifications = tth + (tva) + cont_env_amount + energie_amount

            # Formatting the total amount
            formatted_amount_total = '{:.2f}'.format(ttc_with_modifications).replace('.', ',') + ' ' + str(order.currency_id.symbol)

            # Update tax totals dictionary
            tax_totals['formatted_amount_total'] = formatted_amount_total
            # print("tax_totals['formatted_amount_total']", tax_totals['formatted_amount_total'])
            tax_totals['amount_total'] = ttc_with_modifications
            # print("tax_totals['amount_total']", tax_totals['amount_total'])

            if order.cont_env:
                tax_totals['cont_env_amount'] = cont_env_amount
                tax_totals['cont_env_amount_formatted'] = '{:.2f}'.format(cont_env_amount).replace('.', ',') + ' ' + str(order.currency_id.symbol)
                # print("tax_totals['cont_env_amount_formatted']", tax_totals['cont_env_amount_formatted'])

            if order.energie_return:
                tax_totals['energie_amount'] = energie_amount
                tax_totals['energie_percentage_amount_formatted'] = '{:.2f}'.format(energie_amount).replace(
                    '.', ',') + ' ' + str(order.currency_id.symbol)
                # tax_totals['rg_percentage'] = order.rg_percentage
                # print("tax_totals['energie_percentage_amount_formatted']", tax_totals['energie_percentage_amount_formatted'])

            # Assign the formatted amount total to tax_totals
            tax_totals['custom'] = tax_totals['formatted_amount_total']
            order.tax_totals = tax_totals
           