# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, date, timedelta


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    advance_payment_method = fields.Selection(selection_add=[
        ('contribution_energie', 'Contribution énergétique et Contribution environnementale')], #, ('cont_env_cee', 'Contribution environnementale')
        ondelete={
            'contribution_energie': 'cascade',
            # 'cont_env_cee': 'cascade',
        },
    )
    energie_percentage_amount = fields.Float(string="Taux de Contribution énergétique")
    amount_total = fields.Float(string="Amount Total")
    due_date = fields.Date("Date d'échéance")
    cont_env_amount = fields.Float("Taux de Contribution environnementale")
    cont_env = fields.Boolean(string="Contribution environnementale")
    energie_return = fields.Boolean(string="Contribution énergétique")

    @api.model
    def default_get(self, fields):
        res = super(SaleAdvancePaymentInv, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            sale_order = self.env['sale.order'].browse(active_id)
            date_order = sale_order.date_order
            res.update({
                'cont_env_amount': sale_order.cont_env_amount or 0.0,
                'cont_env': sale_order.cont_env,
                'amount_total': sale_order.amount_total,
                'energie_return': sale_order.energie_return,
                'energie_percentage_amount': sale_order.rg_percentage,
                'due_date': date_order + timedelta(days=365)
            })
        return res

    # def create_invoices(self):
    #     print("advance_payment_method******",self.advance_payment_method)
    #     res = super(SaleAdvancePaymentInv, self).create_invoices()
    #     if self.advance_payment_method not in ['delivered','percentage','fixed']:
    #         print('energie_percentage_amount**********', self.energie_percentage_amount)
    #     else:
    #         res = super(SaleAdvancePaymentInv,self).create_invoices()
    #         return res

    def _create_invoices(self, sale_orders):
        if self.advance_payment_method not in ['contribution_energie']: #'cont_env_cee',
            invoices = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
            rg_account_id = self.env.company.ad_rg_account_id
            account_id = self.env.company.ad_cee_account_id
            product_id = self.env['product.product'].search([('property_account_income_id', '=', account_id.id)],
                                                            limit=1)
            rg_product_id = self.env['product.product'].search([('property_account_income_id', '=', rg_account_id.id)],
                                                               limit=1)
            currency_id = account_id.company_id.currency_id
            for invoice in invoices:
                invoice_line_ids = []
                if self.cont_env:
                    invoice_line_ids.append((0, 0,
                                             {'product_id': product_id.id, 'name': 'Contribution environnementale',
                                              'account_id': account_id.id,
                                              'quantity': 0, 'price_unit': 0, 'tax_ids': False,
                                              'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'ad_is_rg_line': True}))
                if self.energie_return:
                    invoice_line_ids.append((0, 0, {'product_id': rg_product_id.id, 'name': 'RG',
                                                    'account_id': rg_account_id.id,
                                                    'quantity': 0, 'price_unit': 0, 'tax_ids': False,
                                                    'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'ad_is_rg_line': True}))
            if invoice_line_ids:
                invoice.invoice_line_ids = invoice_line_ids
            return invoices
        else:
            if self.advance_payment_method == 'contribution_energie':
                invoices = sale_orders.with_context(active_test=False, contribution_energie=True)._create_invoices(
                    final=self.deduct_down_payments)
                if self.energie_percentage_amount:

                    for invoice in invoices:
                        invoice.rg_percentage = self.energie_percentage_amount
                    # return invoices

            # if self.advance_payment_method == 'cont_env_cee':
            #     invoices = sale_orders.with_context(active_test=False, cont_env_cee=True)._create_invoices(
            #         final=self.deduct_down_payments)
            #     for invoice in invoices:
            #         invoice.cont_env = self.cont_env
            #         if self.cont_env:
            #             invoice.cont_env_amount = self.cont_env_amount
            #         if self.energie_return:
            #             invoice.energie_return = True
                # return invoices
            
            rg_account_id = self.env.company.ad_rg_account_id
            account_id = self.env.company.ad_cee_account_id
            product_id = self.env['product.product'].search([('property_account_income_id', '=', account_id.id)],
                                                            limit=1)
            rg_product_id = self.env['product.product'].search([('property_account_income_id', '=', rg_account_id.id)],
                                                               limit=1)
            currency_id = account_id.company_id.currency_id
            for invoice in invoices:
                invoice.cont_env = self.cont_env
                for invoice in invoices:
                    invoice.cont_env = self.cont_env
                    invoice_line_ids = []
                    # if self.cont_env:
                    invoice.cont_env_amount = self.cont_env_amount
                    if self.cont_env:
                        price_unit = -1 * self.cont_env_amount
                    else:
                        price_unit = 0
                    if self.cont_env:    
                        invoice_line_ids.append((0, 0,
                                                 {'product_id': product_id.id, 'name': 'Contribution environnementale',
                                                  'account_id': account_id.id,
                                                  'quantity': 1.0, 'price_unit': price_unit, 'tax_ids': False,
                                                  'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'ad_is_rg_line': True}))
                    if self.energie_return:
                        rg_price_unit = -1 * self.amount_total * (self.energie_percentage_amount / 100)
                    else:
                        rg_price_unit = 0
                    if self.energie_return:
                        invoice_line_ids.append((0, 0, {'product_id': rg_product_id.id, 'name': 'RG',
                                                        'account_id': rg_account_id.id,
                                                        'quantity': 1.0, 'price_unit': rg_price_unit, 'tax_ids': False,
                                                        'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'ad_is_rg_line': True}))
                if invoice_line_ids:
                    invoice.invoice_line_ids = invoice_line_ids
 
            return invoices
