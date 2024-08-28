
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round
import re

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
LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # frais = fields.Many2many('frais',
    #     string="Frais", readonly=False)
    #
    # frais_amount = fields.Float("Montant Frais", readonly=True)

    order_id_display = fields.Integer(string='Order ID', compute='_compute_order_id_display', store=True)

    def _compute_order_id_display(self):
        for line in self:
            line.order_id_display = line.order_id.id

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

    type_ligne = fields.Selection([
        ('aog', 'AOG'),
        ('code_rouge', 'CODE ROUGE'),
        ('fil_rouge', 'FIL ROUGE'),
        ('Horizon_flexible', 'Horizon flexible'),
        ('Horizon_previsionnel', 'Horizon prévisionnel'),
        ('Appel_de_livraison', 'Appel de livraison'),
        ('Prestation', 'Prestation'),
        ('Retour_Client', 'Retour Client'),
        ('Reparation', 'Réparation'),
        ('COMMANDE_FERME', 'COMMANDE FERME'),
        ('AOG_REPARATION', 'AOG RÉPARATION'),
        ('autres', 'AUTRES')],
        string="Type de la ligne")

    produit_recu_client = fields.Many2one('product.template', string="Produit reçu de la part du client")

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        if self.product_template_id:
            self.produce_delay = self.product_template_id.produce_delay
            self.days_to_prepare_mo = self.product_template_id.days_to_prepare_mo
            self.sale_delay = self.product_template_id.sale_delay
            self.produit_recu_client = self.product_template_id.produit_recu_client

    @api.onchange('type_ligne')
    def _onchange_type_ligne(self):
        if self.type_ligne:
            product = self.env['product.template'].search([('type_frais', '=', self.type_ligne)], limit=1)
            if product:
                self._add_line_with_product(product)
            else:
                return {
                    'warning': {
                        'title': "Produit non trouvé",
                        'message': "Aucun produit avec le type frais correspondant n'a été trouvé."
                    }
                }


    def _add_line_with_product(self, product):
        # Récupération de la commande associée à cette ligne
        order = self.order_id

        if not order:
            raise ValueError("Impossible de trouver la commande associée à cette ligne de commande.")

        order_id = order.id
        print("order", order_id)

        match = re.search(r'NewId_(\d+)', str(order_id))
        print("match", match)

        if match:
            order_id_number = int(match.group(1))
            print("Order ID Number:", order_id_number)
        else:
            print("Order ID format is incorrect.")
            order_id_number = order_id  # Utiliser l'ID tel quel si le format est incorrect

        # Récupération du produit produit.product associé au produit.template
        product_product = self.env['product.product'].search([('product_tmpl_id', '=', product.id)], limit=1)
        if not product_product:
            raise ValueError("Aucun produit product.product associé trouvé pour ce product.template.")

        # Création de la ligne de commande avec product_template_id et les autres champs requis
        order_line = self.env['sale.order.line'].create({
            'order_id': order_id_number,
            'product_template_id': product.id,
            'product_id': product_product.id,  # Obligatoire pour sale.order.line
            'name': product.name + " de " + self.name,
            'product_uom': product.uom_id.id,  # Unité de mesure
            'product_uom_qty': 1,  # Ajustez la quantité selon vos besoins
            'price_unit': product.list_price,  # Vous pouvez ajuster le prix selon vos besoins
        })
        # Ajout de la ligne de commande créée à la commande
        order.order_line += order_line



    date_previsionnelle_reussite = fields.Date(string="Date prévisionnelle de réussite")
    appliquer_seuil_a_la_ligne = fields.Boolean(string="Appliquer la seuil à la ligne de commande", related='product_id.appliquer_seuil_a_la_ligne')
    seuil = fields.Float(string='Seuil à la ligne', related='product_id.montant_seuil_a_la_commande')
    is_threshold_line = fields.Boolean(string="Ligne de seuil", default=False)

    sequence_order = fields.Integer(string='Sequence Order', compute='_compute_sequence_order', store=True)

    # @api.depends('order_id', 'sequence')
    # def _compute_sequence_order(self):
    #     for order in self.mapped('order_id'):
    #         sequence = 1
    #         for line in order.order_line.sorted('sequence'):
    #             line.sequence_order = sequence
    #             sequence += 1

    @api.depends('order_id', 'sequence')
    def _compute_sequence_order(self):
        for order in self.mapped('order_id'):
            sequence = 1
            for line in order.order_line.sorted('sequence'):
                if line.product_id.product_tmpl_id.type_frais:  # Skip lines with type_frais
                    continue
                line.sequence_order = sequence
                sequence += 1
                # print("line.product_template_id.bom_ids", line.product_template_id.bom_ids)

    @api.model
    def create(self, vals):
        record = super(SaleOrderLine, self).create(vals)
        record.appliquer_seuil_si_necessaire()
        return record

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        for record in self:
            record.appliquer_seuil_si_necessaire()
        return res

    def appliquer_seuil_si_necessaire(self):
        for line in self:
            if line.appliquer_seuil_a_la_ligne and line.price_subtotal < line.seuil:
                # Recherche du produit avec type_frais = 'seuil_ligne'
                product = self.env['product.template'].search([('type_frais', '=', 'seuil_ligne')], limit=1)

                if product:
                    order = line.order_id

                    if not order:
                        raise UserError("Impossible de trouver la commande associée à cette ligne de commande.")

                    # Récupération du produit product associé au product template trouvé
                    product_product = self.env['product.product'].search([('product_tmpl_id', '=', product.id)],
                                                                         limit=1)

                    if not product_product:
                        raise UserError("Aucun produit product.product associé trouvé pour ce product.template.")

                    # Vérifier si la ligne de seuil existe déjà pour éviter la duplication
                    existing_seuil_lines = order.order_line.filtered(
                        lambda l: l.product_id == product_product and l.name == product.name + " de " + line.name)
                    if not existing_seuil_lines:
                        # Création de la ligne de commande avec product_template_id et les autres champs requis
                        order_line_vals = {
                            'order_id': order.id,
                            'product_id': product_product.id,  # Obligatoire pour sale.order.line
                            'name': product.name + " de " + line.name,
                            'product_uom': product.uom_id.id,  # Unité de mesure
                            'product_uom_qty': 1,  # Ajustez la quantité selon vos besoins
                            'price_unit': line.seuil - line.price_subtotal,
                            'is_threshold_line': True,
                            # Vous pouvez ajuster le prix selon vos besoins
                        }
                        self.env['sale.order.line'].create(order_line_vals)
                else:
                    raise UserError("Aucun produit avec le type frais correspondant n'a été trouvé.")

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.is_threshold_line:
            res.update({
                'display_type': self.display_type or 'product',
                'sequence': self.sequence,
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.product_uom_qty,
                'price_unit': self.price_unit,
                'tax_ids': [Command.set(self.tax_id.ids)],
                'sale_line_ids': [Command.link(self.id)],
                'is_downpayment': self.is_downpayment,
            })
        return res

    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['sale.order.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
            for frais_tax in product.frais:
                taxes_by_product_company[(product, frais_tax.company_id)] += frais_tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = taxes_by_product_company[(line.product_id, company)]
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

class SaleOrder(models.Model):
    _inherit = "sale.order"

    interlocuteur = fields.Many2one('res.partner', string="Interlocuteur")

    poids_carbone_unit = fields.Float("Poids Carbone unitaire", default=lambda self: self.env.company.poids_carbone.poids_carbone)
    poids_carbone_total = fields.Float("Poids Carbone Total", compute="_compute_poids_carbone_total")
    n_quality = fields.Char("Qualité", related="company_id.n_quality")
    # state = fields.Selection(readonly=False,
    #                          selection_add=[('devis_validee', 'Devis validé'),
    #                                         ('commande_non_traite', 'Commande non traitée'),])

    state = fields.Selection(
        selection=[
            ('draft', "Quotation"),
            ('sent', "Quotation Sent"),
            ('approve', 'à Approuver'),
            ('approve2', 'Approuvé'),
            ('devis_validee', 'Devis validé'),
            ('commande_non_traite', 'Commande non traitée'),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
            ('refuse', 'Refused'),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    def action_devis_validee(self):
        if self:
            for data in self:
                data.state = 'devis_validee'

    def action_commande_non_traite(self):
        if self:
            for data in self:
                data.state = 'commande_non_traite'


    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_poids_carbone_total(self):
        for order in self:
            total_quantity = sum(
                line.product_uom_qty for line in order.order_line if line.product_id.fabrique == True)
            order.poids_carbone_total = total_quantity * order.poids_carbone_unit


    modes_reglement = fields.Many2one('modes.reglement', string="Mode de réglement", related="partner_id.modes_reglement"
                                      ,readonly=True)
    date_reponse = fields.Date(string="Date de réponse")
    appliquer_seuil_a_la_ligne = fields.Boolean(string="Appliquer la seuil à la ligne de commande", required=True)
    seuil_a_la_ligne = fields.Float(string="Seuil à la ligne de commande", related="partner_id.seuil_a_la_ligne")
    custom_order_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        string='Lignes de Commande Personnalisées')

    def send_reminder_email(self):
        template_id = self.env.ref('ad_aero_sale.email_template_reminder').id
        template = self.env['mail.template'].browse(template_id)
        print("template_id",template_id)
        for order in self:
            email_from = order.company_id.email
            email_to = order.partner_id.email
            menu_id = self.env.ref('sale.menu_sale_quotations').id
            action_id = self.env.ref('sale.action_quotations_with_onboarding').id
            so_url = self._make_url(self.id, self._name, menu_id, action_id)

            if email_from and email_to:
                print(f"Sending email from {email_from} to {email_to} for order {order.name}")
                template.sudo().send_mail(order.id, force_send=True)
                email_body = ''' <span style='font-style: 16px;font-weight:
                                  bold;'>Cher, %s</span>''' % (order.partner_id.name) + ''' <br/><br/>
                                  ''' + ''' <span style='font-style: 14px;'> Nous souhaitons vous informer que votre commande n° 
                                  <span style='font-weight: bold;'>%s</span>  expirera dans 30 jours,</span>''' % \
                             (self.env.user.name) + ''' <br/>''' + '''<span
                                       style='font-style: 14px;'>Afin de vous assurer que votre commande soit bien validée avant cette date, nous vous invitons à vérifier les détails de votre commande et à nous contacter si vous avez besoin de plus d'informations ou si vous souhaitez apporter des modifications. 
                                       <br/> Cordialement, </span> <div style="margin-top:40px;"> <a
                                       href="''' + so_url + '''" style="background-color:
                                       #1abc9c; padding: 20px; text-decoration: none; color:
                                        #fff; border-radius: 5px; font-size: 16px;"
                                        class="o_default_snippet_text">Voir Devis</a></div>
                                        <br/><br/>'''
                email_id = self.env['mail.mail']. \
                    sudo().create({'subject': 'Rappel : Votre commande expirera dans 30 jours',
                                   'email_from': email_from,
                                   'email_to': email_to,
                                   'message_type': 'email',
                                   'model': 'sale.order',
                                   'res_id': self.id,
                                   'body_html': email_body
                                   })
                email_id.send()

                # Ajouter un message dans le chatter
                order.message_post(
                    body=f"Reminder email sent to {email_to} for order {order.name}",
                    subject="Order Validity Reminder",
                    message_type='email',
                    subtype_xmlid='mail.mt_note'
                )
            else:
                print(f"Email not sent for order {order.name}. Missing email_from or email_to.")

    @api.model
    def _cron_send_reminder_email(self):
        j_30 = (fields.Date.today() + relativedelta(days=30)).strftime('%Y-%m-%d')
        orders = self.search([('validity_date', '=', j_30)])
        print(f"Orders found with validity_date = {j_30}: {orders}")
        for order in orders:
            order.send_reminder_email()
            print("order.send_reminder_email()",order.send_reminder_email())

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

    # def _prepare_invoice_line(self, line):
    #     res = super(SaleOrder, self)._prepare_invoice_line(line)
    #     if line.is_threshold_line:
    #         res.update({
    #             'name': line.name,
    #             'product_id': line.product_id.id,
    #             'uom_id': line.product_uom.id,
    #             'quantity': line.product_uom_qty,
    #             'price_unit': line.price_unit,
    #         })
    #     return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        for invoice in invoices:
            for order in self:
                for line in order.order_line.filtered(lambda l: l.is_threshold_line):
                    invoice_line_vals = line._prepare_invoice_line()
                    invoice.write({'invoice_line_ids': [(0, 0, invoice_line_vals)]})
        return invoices

    poids_carbone = fields.Float("Poids Carbone")
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            print("Triggering _compute_partner_invoice_id")
            if order.partner_id:
                print("Partner found: ", order.partner_id.name)
                default_invoice_address = self.env['res.partner'].search([
                    ('parent_id', '=', order.partner_id.id),
                    ('address_facturation_par_defaut', '=', True)
                ], limit=1)

                if default_invoice_address:
                    print("Default invoice address found: ", default_invoice_address.name)
                    order.partner_invoice_id = default_invoice_address
                else:
                    print("No default invoice address found, using default Odoo address")
                    order.partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice']
            else:
                order.partner_invoice_id = False

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            if order.partner_id:
                # Rechercher l'adresse de livraison par défaut
                default_shipping_address = self.env['res.partner'].search([
                    ('parent_id', '=', order.partner_id.id),
                    ('address_livraison_par_defaut', '=', True)
                ], limit=1)

                # Si trouvée, l'utiliser; sinon, utiliser l'adresse de livraison par défaut d'Odoo
                if default_shipping_address:
                    order.partner_shipping_id = default_shipping_address
                else:
                    order.partner_shipping_id = order.partner_id.address_get(['delivery'])['delivery']
            else:
                order.partner_shipping_id = False

    def action_confirm(self):
        # Appeler la méthode parente pour confirmer la commande
        res = super(SaleOrder, self).action_confirm()

        # Ensuite, créer un mouvement de stock
        self.create_stock_move()

        return res

    def create_stock_move(self):
        for order in self:
            company = order.company_id

            # Rechercher le picking_type de réception pour la société
            picking_type = self.env['stock.picking.type'].with_context(force_company=company.id).search([
                ('code', '=', 'incoming'),  # Type de réception
                ('warehouse_id.company_id', '=', company.id)
            ], limit=1)

            if not picking_type:
                raise UserError("Le type de picking pour les réceptions n'a pas été trouvé dans la société.")

            # Initialiser des variables pour vérifier si des lignes de commande sont valides
            has_valid_lines = False
            location_src = False
            location_dest = False

            # Vérifiez si au moins une ligne de commande a les champs requis remplis
            for line in order.order_line:
                if (line.product_template_id.emplacement_produit_recu_client and
                        line.product_template_id.emplacement_produit_recu_client_qy and
                        line.product_id.product_tmpl_id.produit_recu_client):
                    # Si nous avons trouvé une ligne valide, mettez à jour les emplacements
                    location_src = line.product_template_id.emplacement_produit_recu_client
                    location_dest = line.product_template_id.emplacement_produit_recu_client_qy
                    has_valid_lines = True
                    break  # Pas besoin de vérifier les autres lignes

            if not has_valid_lines:
                raise UserError(
                    "Aucune ligne de commande ne contient les champs 'location_src', 'location_dest' et 'produit_recu_client' remplis.")

            if not location_src or not location_dest:
                raise UserError("Les emplacements 'Entrée' ou 'Stock' n'ont pas été trouvés dans la société.")

            # Créer ou récupérer un procurement group pour la commande de vente
            procurement_group = self.env['procurement.group'].search([
                ('sale_id', '=', order.id),
            ], limit=1)
            if not procurement_group:
                procurement_group = self.env['procurement.group'].create({
                    'name': order.name,
                    'sale_id': order.id,
                })

            # Créer le picking (bon d'entrée)
            picking_vals = {
                'partner_id': order.partner_id.id,
                'picking_type_id': picking_type.id,  # Utiliser le picking_type de réception
                'location_id': location_src.id,  # Emplacement 'Entrée' comme source
                'location_dest_id': location_dest.id,  # Emplacement 'Stock' comme destination
                'picking_type_code': 'incoming',
                'origin': order.name,
                'company_id': company.id,
                'sale_id': order.id,
                'group_id': procurement_group.id,
            }
            picking = self.env['stock.picking'].create(picking_vals)

            # Associer le picking à la commande de vente
            order.write({
                'picking_ids': [(4, picking.id)]
            })

            # Créer les mouvements de stock pour chaque ligne de commande
            for line in order.order_line:
                if (line.product_template_id.emplacement_produit_recu_client and
                        line.product_template_id.emplacement_produit_recu_client_qy and
                        line.product_id.product_tmpl_id.produit_recu_client):
                    move_vals = {
                        'name': line.name,
                        'product_id': line.product_id.product_tmpl_id.produit_recu_client.product_variant_id.id,
                        'product_uom_qty': line.product_uom_qty,  # Ajouter la quantité
                        'product_uom': line.product_uom.id,
                        'picking_id': picking.id,
                        'location_id': location_src.id,
                        'location_dest_id': location_dest.id,
                        'company_id': company.id,
                        'state': 'draft',
                        'group_id': procurement_group.id,
                        'sale_line_id': line.id,
                    }
                    print("line.product_id.product_tmpl_id.produit_recu_client.id",
                          line.product_id.product_tmpl_id.produit_recu_client.id)
                    stock_move = self.env['stock.move'].create(move_vals)
                    stock_move_line_vals = {
                        'move_id': stock_move.id,
                        'product_id': line.product_id.product_tmpl_id.produit_recu_client.product_variant_id.id,
                        'qty_done': line.product_uom_qty,  # qty_done égale à product_uom_qty
                        'product_uom_id': line.product_id.product_tmpl_id.produit_recu_client.product_variant_id.uom_id.id,
                        'location_id': location_src.id,
                        'location_dest_id': location_dest.id,
                        'company_id': company.id,
                    }
                    self.env['stock.move.line'].create(stock_move_line_vals)

            # Confirmer et valider le picking (décommentez si nécessaire)
            # picking.action_confirm()
            # picking.button_validate()  # Valider le picking

            # Retourner l'action pour ouvrir la vue du picking créé
            return {
                'type': 'ir.actions.act_window',
                'name': 'Inventory Overview',
                'res_model': 'stock.picking',
                'res_id': picking.id,
                'view_mode': 'form',
                'target': 'current',
            }


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"




class AccountMove(models.Model):
    _inherit = "account.move"

    seuil_a_la_ligne = fields.Float(string="Seuil à la ligne de commande", readonly=False,
                                    related="partner_id.seuil_a_la_ligne")

