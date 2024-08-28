# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import frozendict

from collections import defaultdict
import math
import re



class AccountTax(models.Model):
    _inherit = 'account.tax'

    frais = fields.Boolean("Frais")
    type_frais = fields.Selection([('client', 'Client'),
                                   ('article', 'Article'),
                                   ('vente', 'Vente'),
                                   ('seuil', 'Seuil à la ligne'),
                                   # ('aog', 'AOG'),
                                   # ('code_rouge', 'CODE ROUGE'),
                                   # ('fil_rouge', 'FIL ROUGE'),
                                   ],)

    product_id = fields.Many2many('product.template', string="Produits")
    product_ids = fields.Many2one('product.template', string="Produit")
    amount_frais_type = fields.Selection(default='percent', string="Calcul du frais", required=True,
                                   selection=[('fixed', 'Fixe'),
                                              ('percent', 'Pourcentage du prix'),],)

    @api.onchange('amount_frais_type')
    def _onchange_amount_frais_type(self):
        if self.amount_frais_type == 'fixed':
            self.amount_type = 'fixed'
        elif self.amount_frais_type == 'percent':
            self.amount_type = 'percent'

    @api.constrains('invoice_repartition_line_ids', 'refund_repartition_line_ids')
    def _validate_repartition_lines(self):
        for record in self:
            # if the tax is an aggregation of its sub-taxes (group) it can have no repartition lines
            if record.amount_type == 'group' and \
                    not record.invoice_repartition_line_ids and \
                    not record.refund_repartition_line_ids:
                continue

            invoice_repartition_line_ids = record.invoice_repartition_line_ids.sorted()
            refund_repartition_line_ids = record.refund_repartition_line_ids.sorted()
            record._check_repartition_lines(invoice_repartition_line_ids)
            record._check_repartition_lines(refund_repartition_line_ids)

            if not record.frais:
                if len(invoice_repartition_line_ids) != len(refund_repartition_line_ids):
                    raise ValidationError(_("Invoice and credit note distribution should have the same number of lines."))

            if not record.frais:
                if not invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax') or \
                        not refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax'):
                    raise ValidationError(
                        _("Invoice and credit note repartition should have at least one tax repartition line."))
            if not record.frais:
                index = 0
                while index < len(invoice_repartition_line_ids):
                    inv_rep_ln = invoice_repartition_line_ids[index]
                    ref_rep_ln = refund_repartition_line_ids[index]

                    if inv_rep_ln.repartition_type != ref_rep_ln.repartition_type or inv_rep_ln.factor_percent != ref_rep_ln.factor_percent:

                        raise ValidationError(
                            _("Invoice and credit note distribution should match (same percentages, in the same order)."))
                    index += 1

    @api.model
    def create(self, vals):
        tax = super(AccountTax, self).create(vals)
        if 'product_id' in vals:
            for tax in self:
                self._update_product_frais(tax.product_id.ids, tax, add=tax.frais)
                self._update_product_fees(tax.product_id.ids, tax, add=tax.frais)
        return tax

    def write(self, vals):
        res = super(AccountTax, self).write(vals)
        if 'product_id' in vals:
            for tax in self:
                self._update_product_frais(tax.product_id.ids, tax, add=tax.frais)
                self._update_product_fees(self.product_id.ids, self, add=self.frais)

        return res

    def _update_product_frais(self, product_ids, tax, add=True):
        products = self.env['product.template'].browse(product_ids)
        for product in products:
            if add:
                product.frais = [(4, tax.id)]
            else:
                product.frais = [(3, tax.id)]

    def _update_product_fees(self, product_ids, tax, add=True):
        products = self.env['product.template'].browse(product_ids)
        for product in products:
            if add:
                product.product_fees_ids = [(0, 0, {
                    'partner_id': product.client.id,  # Remplacez <partner_id> par l'ID du partenaire approprié
                    'frais': tax.id,})]
            else:
                fees_to_remove = product.product_fees_ids.filtered(lambda fee: fee.frais == tax.id)
                fees_to_remove.unlink()

    def unlink(self):
        for tax in self:
            product_ids = tax.product_id.ids
            res = super(AccountTax, self).unlink()
            # Supprimer les frais associés des produits
            products = self.env['product.template'].browse(product_ids)
            for product in products:
                product.product_fees_ids.filtered(lambda fee: fee.frais.id == tax.id).unlink()
        return res

    @api.constrains('product_ids')
    def _check_product_ids_unique(self):
        for tax in self:
            if tax.product_ids:
                # Rechercher d'autres taxes associées à ce produit
                other_taxes = self.search([('id', '!=', tax.id), ('product_ids', '=', tax.product_ids.id)])
                if other_taxes:
                    raise ValidationError(f"Le produit {tax.product_ids.name} est déjà associé à un autre Frais.")

    # @api.constrains('type_frais')
    # def _check_type_frais_unique(self):
    #     for type in self:
    #         if type.type_frais:
    #             # Rechercher d'autres frais associés à ce produit
    #             aog_type = self.search([('id', '!=', type.id), ('type_frais', '=', 'aog')])
    #             if aog_type:
    #                 raise ValidationError("Le type du frais 'AOG' existe déjà.")
    #             code_rouge_type = self.search([('id', '!=', type.id), ('type_frais', '=', 'code_rouge')])
    #             if code_rouge_type:
    #                 raise ValidationError("Le type du frais 'Code Rouge' existe déjà.")
    #             fil_rouge_type = self.search([('id', '!=', type.id), ('type_frais', '=', 'fil_rouge')])
    #             if fil_rouge_type:
    #                 raise ValidationError("Le type du frais 'Fil Rouge' existe déjà.")




class PartnerProductFees(models.Model):
    _name = 'partner.product.fees'
    _description = 'Partner Product Fees'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    product_id = fields.Many2one('product.template', string='Product', required=True)
    frais = fields.Many2one('account.tax', string='Frais', domain="[('frais', '=', True)]", required=True)
    type_frais = fields.Selection(string="Type du frais", related="frais.type_frais")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)