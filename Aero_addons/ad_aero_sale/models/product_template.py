# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    first_bom_operation_ids = fields.One2many(
        'mrp.routing.workcenter',
        string="Opérations",
        compute='_compute_first_bom_operations'
    )
    durcisseur = fields.Boolean("Durcisseur")
    diluant = fields.Boolean("Diluant")
    base = fields.Boolean("Base")

    @api.depends('bom_ids')
    def _compute_first_bom_operations(self):
        for product in self:
            # Trouver la première nomenclature (mrp.bom) liée au produit
            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)], limit=1)

            if bom:
                # Si une nomenclature est trouvée, récupérer les `operation_ids` de cette nomenclature
                product.first_bom_operation_ids = bom.operation_ids
            else:
                product.first_bom_operation_ids = False


    frais = fields.Many2many('account.tax',
                             string="Frais", readonly=False, domain= "[('frais', '=', True)]",)
    fai = fields.Boolean(string="Article FAI")


    montant_seuil_a_la_commande = fields.Float(string="Montant de seuil à la ligne de commande", related="client.seuil_a_la_ligne")
    appliquer_seuil_a_la_ligne = fields.Boolean(string="Appliquer la seuil à la ligne de commande")
    frais_seuil_a_la_commande = fields.Many2one('account.tax', string="Frais seuil à la ligne", compute='_compute_frais_seuil')

    last_order_date = fields.Date(string="Date de la dernière commande", compute='_compute_last_order_date')
    order_line_ids = fields.One2many('sale.order.line', 'product_template_id', string='Order Lines')

    days_since_last_order = fields.Integer(string="Nombre de jours depuis la dernière commande",
                                           compute='_compute_days_since_last_order', store=True)

    type_frais = fields.Selection([('aog', 'AOG'),
                                   ('code_rouge', 'CODE ROUGE'),
                                   ('fil_rouge', 'FIL ROUGE'),
                                   ('seuil_ligne', 'Seuil à la ligne'),
                                   ], string="Type frais")

    fabrique = fields.Boolean(string='Fabriqué', compute="check_bom_and_update")

    produit_recu_client = fields.Many2one('product.template', string="Produit reçu de la part du client")
    emplacement_produit_recu_client = fields.Many2one(
        'stock.location', "Emplacement du produit reçu client",
        company_dependent=True, check_company=True,
        domain="[('usage', '=', 'supplier'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",)

    emplacement_produit_recu_client_qy = fields.Many2one(
        'stock.location', "Emplacement du contrôle du produit reçu client",
        company_dependent=True, check_company=True,
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",)

    emplacement_produit_recu_client_stock = fields.Many2one(
        'stock.location', "Emplacement du produit reçu client dans le stock",
        company_dependent=True, check_company=True,
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",)


    def check_bom_and_update(self):
        for product in self:

            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)], limit=1)

            if bom:
                product.fabrique = True
            else:
                product.fabrique = False


    @api.constrains('type_frais')
    def _check_unique_type_frais(self):
        for record in self:
            if record.type_frais:
                existing_products = self.search([('type_frais', '=', record.type_frais), ('id', '!=', record.id)])
                if existing_products:
                    raise ValidationError(
                        f"Un autre produit contient déjà le type de frais '{record.type_frais}'. Un seul produit peut avoir ce type de frais.")

    @api.depends('frais')  # Assurez-vous que le champ qui lie les taxes au produit est 'taxes_id'
    def _compute_frais_seuil(self):
        for rec in self:
            # Recherche la première taxe associée au produit (si plusieurs, vous pouvez ajuster la logique)
            frais = rec.env['account.tax'].search([('product_ids', '=', rec.id)], limit=1)
            rec.frais_seuil_a_la_commande = frais if frais else False

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res._compute_frais_seuil()
        return res

    def write(self, vals):
        if not self.env.context.get('skip_write'):
            self = self.with_context(skip_write=True)
            return super(ProductTemplate, self).write(vals)
        # res = super(ProductTemplate, self).write(vals)
        # self._compute_frais_seuil()
        # return res

    # frais_aog = fields.Many2many('account.tax',
    #                          string="Frais AOG", readonly=False, domain="[('frais', '=', True)]", )
    # frais_code_rouge = fields.Many2many('account.tax',
    #                          string="Frais code rouge", readonly=False, domain="[('frais', '=', True)]", )
    # frais_fil_rouge = fields.Many2many('account.tax',
    #                          string="Frais fil rouge", readonly=False, domain="[('frais', '=', True)]", )

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
        # print("non")
        # if self.days_since_last_order > 1:
        #     print("yes")
        products_to_update = self.search([('days_since_last_order', '>', 180)])
        # print("products_to_update",products_to_update)
        for product in products_to_update:
            product.sale_line_warn = 'block'
            product.sale_line_warn_msg = "La vente de ce produit est bloquée car le nombre de jours depuis la dernière commande dépasse 180 jours."

    @api.onchange('client')
    def apply_client_fees(self):
        product_id_number = 0
        product = self.id
        # print("order", product)

        match = re.search(r'NewId_(\d+)', str(product))
        # print("match", match)

        if match:
            product_id_number = int(match.group(1))
            # print("product ID Number:", product_id_number)
        else:
            # print("product ID format is incorrect.")
            product_id_number = product  # Utiliser l'ID tel quel si le format est incorrect

        if self.client:
            partner_frais = self.client.frais
            frais_fai = self.client.frais_fai
            frais_frais_lancement = self.client.frais_lancement
            if partner_frais:
                # Combine existing frais with the ones from the client
                self.frais |= partner_frais

            if frais_fai and self.fai:
                self.frais |= frais_fai
            bom_exists = int(self.env['mrp.bom'].search([('product_tmpl_id', '=', product_id_number)]))>0

            if frais_frais_lancement:

                if bom_exists:
                    self.frais |= frais_frais_lancement



    n_poste_client = fields.Char(string="N° poste client")
    n_dossier = fields.Char(string="N° dossier")
    n_contrat = fields.Char(string="N° de contrat")
    qte_previsionnelle_marche = fields.Integer(string="Qte prévisionnelle du marché")
    cycle_production_estimatif = fields.Integer(string="Cycle de production estimatif ")
    taux_previsionnel_reussite = fields.Float(string="Taux de prévisionnel réussite")
    product_fees_ids = fields.One2many('partner.product.fees', 'product_id', string='Frais')

    @api.onchange('product_fees_ids')
    def _onchange_product_fees_ids(self):
        self._compute_frais()

    @api.depends('product_fees_ids')
    def _compute_frais(self):
        for product in self:
            frais_ids = product.product_fees_ids.mapped('frais.id')
            product.frais = [(6, 0, frais_ids)]


    # @api.model
    # def write(self, values):
    #     product = super(ProductTemplate, self).write(values)
    #     if 'frais' in values:
    #         product.update_frais()
    #     return product
    #
    # @api.depends('frais')
    # def update_frais(self):
    #     for product in self:
    #         print("yes")
    #         product.product_fees_ids = [(0, 0, {
    #             'partner_id': product.client.id,
    #             'frais': frais.id,
    #         }) for frais in product.frais]
