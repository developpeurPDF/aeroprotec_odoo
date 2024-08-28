# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, date, timedelta


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    advance_payment_method = fields.Selection(selection_add=[
        ('retenue_de_garantie', 'Contribution énergétique'), ('prime_cee', 'Contribution environnementale')],
        ondelete={
            'retenue_de_garantie': 'cascade',
            'prime_cee': 'cascade',
        },
    )
    guarantee_percentage_amount = fields.Float(string="Taux de Contribution énergétique")
    amount_total = fields.Float(string="Amount Total")
    due_date = fields.Date("Date d'échéance")
    prime_amount = fields.Float("Taux de Contribution environnementale")
    prime = fields.Boolean(string="Contribution environnementale")
    guarantee_return = fields.Boolean(string="Contribution énergétique")

    @api.model
    def default_get(self, fields):
        res = super(SaleAdvancePaymentInv, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            sale_order = self.env['sale.order'].browse(active_id)
            date_order = sale_order.date_order
            res.update({
                'prime_amount': sale_order.prime_amount or 0.0,
                'prime': sale_order.prime,
                'amount_total': sale_order.amount_total,
                'guarantee_return': sale_order.guarantee_return,
                'guarantee_percentage_amount': sale_order.rg_percentage,
                'due_date': date_order + timedelta(days=365)
            })
        return res

    # def create_invoices(self):
    #     print("advance_payment_method******",self.advance_payment_method)
    #     res = super(SaleAdvancePaymentInv, self).create_invoices()
    #     if self.advance_payment_method not in ['delivered','percentage','fixed']:
    #         print('guarantee_percentage_amount**********', self.guarantee_percentage_amount)
    #     else:
    #         res = super(SaleAdvancePaymentInv,self).create_invoices()
    #         return res

    def _create_invoices(self, sale_orders):
        if self.advance_payment_method not in ['prime_cee', 'retenue_de_garantie']:
            invoices = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
            rg_account_id = self.env.company.acs_rg_account_id
            account_id = self.env.company.acs_cee_account_id
            product_id = self.env['product.product'].search([('property_account_income_id', '=', account_id.id)],
                                                            limit=1)
            rg_product_id = self.env['product.product'].search([('property_account_income_id', '=', rg_account_id.id)],
                                                               limit=1)
            currency_id = account_id.company_id.currency_id
            for invoice in invoices:
                invoice_line_ids = []
                if self.prime:
                    invoice_line_ids.append((0, 0,
                                             {'product_id': product_id.id, 'name': 'Contribution environnementale',
                                              'account_id': account_id.id,
                                              'quantity': 0, 'price_unit': 0, 'tax_ids': False,
                                              'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'acs_is_rg_line': True}))
                if self.guarantee_return:
                    invoice_line_ids.append((0, 0, {'product_id': rg_product_id.id, 'name': 'RG',
                                                    'account_id': rg_account_id.id,
                                                    'quantity': 0, 'price_unit': 0, 'tax_ids': False,
                                                    'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'acs_is_rg_line': True}))
            if invoice_line_ids:
                invoice.invoice_line_ids = invoice_line_ids
            return invoices
        else:
            if self.advance_payment_method == 'retenue_de_garantie':
                invoices = sale_orders.with_context(active_test=False, retenue_de_garantie=True)._create_invoices(
                    final=self.deduct_down_payments)
                if self.guarantee_percentage_amount:

                    for invoice in invoices:
                        invoice.rg_percentage = self.guarantee_percentage_amount
                    # return invoices

            if self.advance_payment_method == 'prime_cee':
                invoices = sale_orders.with_context(active_test=False, prime_cee=True)._create_invoices(
                    final=self.deduct_down_payments)
                for invoice in invoices:
                    invoice.prime = self.prime
                    if self.prime:
                        invoice.prime_amount = self.prime_amount
                    if self.guarantee_return:
                        invoice.guarantee_return = True
                # return invoices
            
            rg_account_id = self.env.company.acs_rg_account_id
            account_id = self.env.company.acs_cee_account_id
            product_id = self.env['product.product'].search([('property_account_income_id', '=', account_id.id)],
                                                            limit=1)
            rg_product_id = self.env['product.product'].search([('property_account_income_id', '=', rg_account_id.id)],
                                                               limit=1)
            currency_id = account_id.company_id.currency_id
            for invoice in invoices:
                invoice.prime = self.prime
                for invoice in invoices:
                    invoice.prime = self.prime
                    invoice_line_ids = []
                    # if self.prime:
                    invoice.prime_amount = self.prime_amount
                    if self.prime:
                        price_unit = -1 * self.prime_amount
                    else:
                        price_unit = 0
                    if self.prime:    
                        invoice_line_ids.append((0, 0,
                                                 {'product_id': product_id.id, 'name': 'Contribution environnementale',
                                                  'account_id': account_id.id,
                                                  'quantity': 1.0, 'price_unit': price_unit, 'tax_ids': False,
                                                  'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'acs_is_rg_line': True}))
                    if self.guarantee_return:
                        rg_price_unit = -1 * self.amount_total * (self.guarantee_percentage_amount / 100)
                    else:
                        rg_price_unit = 0
                    if self.guarantee_return:
                        invoice_line_ids.append((0, 0, {'product_id': rg_product_id.id, 'name': 'RG',
                                                        'account_id': rg_account_id.id,
                                                        'quantity': 1.0, 'price_unit': rg_price_unit, 'tax_ids': False,
                                                        'price_subtotal': 0.0, 'currency_id': 1, 'display_type': 'product', 'acs_is_rg_line': True}))
                if invoice_line_ids:
                    invoice.invoice_line_ids = invoice_line_ids
 
            return invoices
