
from collections import defaultdict
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round

from odoo import api, fields, models, _
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    is_html_empty,
    sql
)



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    frais = fields.Many2many('frais',
        string="Frais", readonly=False)

    frais_amount = fields.Float("Montant Frais", readonly=True)

    n_poste_client = fields.Char(string="N° poste client")
    n_dossier = fields.Char(string="N° dossier")
    n_contrat = fields.Char(string="N° de contrat")
    qte_previsionnelle_marche = fields.Integer(string="Qte prévisionnelle du marché")
    cycle_production_estimatif = fields.Integer(string="Cycle de production estimatif ")
    taux_previsionnel_reussite = fields.Float(string="Taux de prévisionnel réussite")
    statut_ligne = fields.Selection([
        ('attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé')],string="Statut de la ligne")

    date_previsionnelle_reussite = fields.Date(string="Date prévisionnelle de réussite")


    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.frais |= self.product_id.frais
            self.n_poste_client = self.product_id.n_poste_client
            self.n_dossier = self.product_id.n_dossier
            self.n_contrat = self.product_id.n_contrat
            self.qte_previsionnelle_marche = self.product_id.qte_previsionnelle_marche
            self.cycle_production_estimatif = self.product_id.cycle_production_estimatif
            self.taux_previsionnel_reussite = self.product_id.taux_previsionnel_reussite



    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'frais.amount', 'frais.type_frais')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line including frais.
        """
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            frais_amount = 0.0
            for frais in line.frais:
                if frais.type_frais == 'percentage':
                    frais_amount += frais.amount / 100 * line.price_unit * line.product_uom_qty
                elif frais.type_frais == 'fixed':
                    frais_amount += frais.amount

            # Include frais_amount in tax computation
            amount_tax += line.tax_id.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                                                  line.order_id.currency_id, line.product_uom_qty)['taxes'][0][
                'amount'] if line.tax_id else 0.0
            line.update({
                'price_subtotal': amount_untaxed + frais_amount,
                'frais_amount': frais_amount,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax + frais_amount,
            })



                
class SaleOrder(models.Model):
    _inherit = "sale.order"

    frais_client = fields.Boolean(string="Appliquer les frais client")
    frais_sale_order = fields.Many2many('frais',
                             string="Frais de priorité", readonly=False,
                             domain= "[('priorite', '=', 'oui')]", )

    appliquer_seuil_a_la_ligne = fields.Boolean(string="Appliquer la seuil à la ligne de commande", required=True)
    seuil_a_la_ligne = fields.Float(string="Seuil à la ligne de commande", related="partner_id.seuil_a_la_ligne")

    def apply_threshold(self):
        for line in self.order_line:
            if line.price_subtotal < self.partner_id.seuil_a_la_ligne:
                line.price_subtotal = self.partner_id.seuil_a_la_ligne
                print("line.frais_amount",line.frais_amount)

    @api.onchange('appliquer_seuil_a_la_ligne')
    def onchange_appliquer_seuil_a_la_ligne(self):
        if self.appliquer_seuil_a_la_ligne:
            self.apply_threshold()

    @api.model
    def create(self, values):
        order = super(SaleOrder, self).create(values)
        if order.appliquer_seuil_a_la_ligne:
            order.apply_threshold()
        return order

    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if 'appliquer_seuil_a_la_ligne' in values and values['appliquer_seuil_a_la_ligne']:
            self.apply_threshold()
        return res


    @api.onchange('frais_client')
    def apply_client_fees(self):
        partner_frais = self.partner_id.frais
        if self.frais_client:
            for line in self.order_line:
                line.frais |= partner_frais

    @api.onchange('frais_sale_order')
    def apply_frais_sale_order(self):
        if self.frais_sale_order:
            for line in self.order_line:
                line.frais |= self.frais_sale_order

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'order_line.frais_amount', 'amount_total',
                 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            tax_base_lines = []
            for line in order_lines:
                tax_base_line = line._convert_to_tax_base_line_dict()
                if self.appliquer_seuil_a_la_ligne:
                    tax_base_line[
                        'price_unit'] = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else line.price_subtotal
                    tax_base_lines.append(tax_base_line)
                else:
                    tax_base_line[
                        'price_unit'] += line.frais_amount / line.product_uom_qty if line.product_uom_qty else line.frais_amount
                    tax_base_lines.append(tax_base_line)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                tax_base_lines,
                order.currency_id or order.company_id.currency_id,
            )

    # def _prepare_invoice(self):
    #     invoice_vals = super(SaleOrder, self)._prepare_invoice()
    #
    #     invoice_vals['autoliquidation'] = self.autoliquidation
    #
    #     return invoice_vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    frais = fields.Float("Frais", readonly=True, compute='_compute_frais')

    @api.depends('sale_line_ids.frais.amount', 'sale_line_ids.frais.type_frais', 'quantity', 'price_unit')
    def _compute_frais(self):
        for line in self:
            frais_amount = 0.0
            for sale_line in line.sale_line_ids:
                for frais in sale_line.frais:
                    if frais.type_frais == 'percentage':
                        frais_amount += frais.amount / 100 * sale_line.price_unit * sale_line.product_uom_qty
                    elif frais.type_frais == 'fixed':
                        frais_amount += frais.amount
            line.frais = frais_amount

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'frais')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False

            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
            subtotal = line.quantity * line_discount_price_unit

            # Compute frais amount.
            frais_amount = line.frais or 0.0

            # Add frais amount to subtotal.
            subtotal += frais_amount

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded'] + frais_amount
                line.price_total = taxes_res['total_included'] + frais_amount
            else:
                line.price_total = line.price_subtotal = subtotal


class AccountMove(models.Model):
    _inherit = "account.move"

    seuil_a_la_ligne = fields.Float(string="Seuil à la ligne de commande", readonly=False,
                                    related="partner_id.seuil_a_la_ligne")