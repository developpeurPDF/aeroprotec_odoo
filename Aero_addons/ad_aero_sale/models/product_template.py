# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, exceptions
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     product_id = fields.Many2one('product.template', string='Product')

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    frais = fields.Many2many('frais',
                             string="Frais", readonly=False, domain= "[('frais_facturation', '!=', 'oui'), ('frais_client', '!=', 'oui'),]",)

    montant_seuil_a_la_commande = fields.Float(string="Montant de seuil à la ligne de commande")

    last_order_date = fields.Date(string="Date de la dernière commande", compute='_compute_last_order_date')
    order_line_ids = fields.One2many('sale.order.line', 'product_template_id', string='Order Lines')

    days_since_last_order = fields.Integer(string="Nombre de jours depuis la dernière commande",
                                           compute='_compute_days_since_last_order', store=True)

    @api.depends('order_line_ids.order_id.date_order')
    def _compute_days_since_last_order(self):
        for product in self:
            last_order_date = False
            for order_line in product.order_line_ids:
                if order_line.order_id.state in ['sale', 'done']:
                    if not last_order_date or order_line.order_id.date_order > last_order_date:
                        last_order_date = order_line.order_id.date_order

            if last_order_date:
                days_since_last_order = (datetime.now() - last_order_date).days
                product.days_since_last_order = days_since_last_order
            else:
                product.days_since_last_order = 0

    @api.depends('order_line_ids.order_id.date_order')
    def _compute_last_order_date(self):
        for product in self:
            last_order_date = False
            for order_line in product.order_line_ids:
                if order_line.order_id.state in ['sale', 'done']:
                    if not last_order_date or order_line.order_id.date_order > last_order_date:
                        last_order_date = order_line.order_id.date_order
            product.last_order_date = last_order_date

    @api.model
    def _cron_update_sale_warnings(self):
        products_to_update = self.search([('days_since_last_order', '>', 180)])
        for product in products_to_update:
            product.sale_line_warn = 'block'
            product.sale_line_warn_msg = "La vente de ce produit est bloquée car le nombre de jours depuis la dernière commande dépasse 180 jours."


    @api.onchange('client')
    def apply_client_fees(self):
        if self.client:
            partner_frais = self.client.frais
            if partner_frais:
                # Combine existing frais with the ones from the client
                self.frais = [(6, 0, partner_frais.ids)]

    n_poste_client = fields.Char(string="N° poste client")
    n_dossier = fields.Char(string="N° dossier")
    n_contrat = fields.Char(string="N° de contrat")
    qte_previsionnelle_marche = fields.Integer(string="Qte prévisionnelle du marché")
    cycle_production_estimatif = fields.Integer(string="Cycle de production estimatif ")
    taux_previsionnel_reussite = fields.Float(string="Taux de prévisionnel réussite")
