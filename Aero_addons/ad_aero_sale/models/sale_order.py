
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round
import re

from odoo import api, fields, models, _

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bon_reception = fields.Boolean(string="B. recp", help="Cocher la case si vous voulez créer un bon réception de matière primaire pour ce produit")
    ref_gamme = fields.Char("Réf Gamme", compute="get_ref_gamme")
    ref_plan = fields.Char("Réf Plan", compute="get_ref_gamme")
    fai = fields.Boolean("FAI", compute="get_ref_gamme")

    @api.depends('product_template_id')
    def get_ref_gamme(self):
        for rec in self:
            # Initialiser la valeur par défaut
            rec.ref_gamme = "---"
            rec.ref_plan = "---"
            rec.fai = False
            # move_ids = rec.product_template_id
            if rec.product_template_id:
                product = rec.product_template_id
                rec.ref_plan = product.plan_reference
                rec.fai = product.fai
                if product.bom_ids:
                    if product.bom_ids[0].code:
                        rec.ref_gamme = product.bom_ids[0].code

    order_id_display = fields.Integer(string='Order ID', compute='_compute_order_id_display', store=True)


    def _compute_order_id_display(self):
        for line in self:
            line.order_id_display = line.order_id.id

    date_recale = fields.Date(String="Date recalée")
    date_livraison = fields.Datetime(String="Date livraison", compute="_compute_delivery_date")

    @api.depends('delivery_dates')
    def _compute_delivery_date(self):
        for rec in self:

            if rec.delivery_dates and rec.sale_delay:
                final_date = self._calculate_final_date(
                    rec.delivery_dates,
                    (rec.sale_delay + rec.days_to_prepare_mo)
                )
                rec.date_livraison = final_date
            elif rec.delivery_dates and rec.produce_delay:
                final_date = self._calculate_final_date(
                    rec.delivery_dates,
                    (rec.days_to_prepare_mo + rec.produce_delay)
                )
                rec.date_livraison = final_date
            else:
                rec.date_livraison = None

    last_mo_date = fields.Datetime(string='Date dernière fabrication', compute='_compute_last_mo_date', store=True)

    @api.depends('product_id')
    def _compute_last_mo_date(self):
        for line in self:
            # Rechercher les ordres de fabrication liés au produit de cette ligne de commande
            manufacturing_orders = self.env['mrp.production'].search([
                ('product_id', '=', line.product_id.id),
                ('state', 'in', ['done', 'progress']),
            ], order='date_planned_start desc', limit=1)

            if manufacturing_orders:
                line.last_mo_date = manufacturing_orders.date_planned_start
            else:
                line.last_mo_date = False


    n_of_interne = fields.Many2one("mrp.production", string="N OF Interne", compute="_compute_n_of_interne")

    @api.depends('order_id', 'product_id')
    def _compute_n_of_interne(self):
        for line in self:
            # Recherche de l'ordre de fabrication correspondant à la ligne de commande
            mrp_production = self.env['mrp.production'].search([
                ('origin', '=', line.order_id.name),
                ('product_id', '=', line.product_id.id)
            ], limit=1)
            line.n_of_interne = mrp_production if mrp_production else False
            if line.n_of_interne:
                # Recherche de la dernière opération de travail en cours dans l'ordre de fabrication
                work_orders = self.env['mrp.workorder'].search([
                    ('production_id', '=', line.n_of_interne.id),
                    ('state', 'in', ['ready', 'progress'])
                ], order='id desc', limit=1)

                

                # Si une opération est trouvée, l'associer à la ligne de commande
                line.last_work_operation = work_orders if work_orders else False

                # Récupérer le poste de travail lié à l'opération
                line.workcenter_id = work_orders.workcenter_id if work_orders else False
            else:
                line.last_work_operation = False
                line.workcenter_id = False

            if line.n_of_interne:
                # Total des opérations
                total_operations = self.env['mrp.workorder'].search_count([
                    ('production_id', '=', line.n_of_interne.id)
                ])

                # Opérations réalisées
                completed_operations = self.env['mrp.workorder'].search_count([
                    ('production_id', '=', line.n_of_interne.id),
                    ('state', '=', 'done')
                ])

                # Mise à jour des champs
                line.total_operations = total_operations
                line.completed_operations = completed_operations
                line.operation_progress = f"{completed_operations} / {total_operations}"
            else:
                line.total_operations = 0
                line.completed_operations = 0
                line.operation_progress = "0 / 0"

    last_work_operation = fields.Many2one('mrp.workorder', string="Dernière opération en cours",
                                          compute="_compute_n_of_interne", store=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string="Poste de travail", compute="_compute_n_of_interne", store=True)

    total_operations = fields.Integer(string="Nombre d'opérations total", compute="_compute_n_of_interne",
                                      store=True)
    completed_operations = fields.Integer(string="Nombre d'opérations réalisées", compute="_compute_n_of_interne",
                                          store=True)
    operation_progress = fields.Char(string="Opérations réalisées / Opérations total",
                                     compute="_compute_n_of_interne", store=True)

    commentaire = fields.Char("Commentaire")

    id_bl = fields.Many2one('stock.picking', string="ID BL", compute="_compute_state_commande", store=True)

    
    

    state_commande = fields.Selection([
        ('R', 'Réceptionné'),
        ('C', 'En cours'),
        ('L', 'Livrée'),
        ('F', 'Facturée')
    ], string="État de la commande", compute="_compute_state_commande", store=True)

    @api.depends('product_uom_qty', 'qty_delivered', 'qty_invoiced', 'order_id', 'order_id.picking_ids')
    def _compute_state_commande(self):
        for line in self:
            order = line.order_id

            # 1- Si qty_invoiced > 0 donc État de la commande = F : facturée
            if line.qty_invoiced > 0:
                line.state_commande = 'F'

            # 2- Si 0 < qty_delivered < product_uom_qty donc État de la commande = C : en cours
            elif 0 < line.qty_delivered < line.product_uom_qty:
                line.state_commande = 'C'

            # 3- Si qty_delivered = product_uom_qty donc État de la commande = L : livrée
            elif line.qty_delivered == line.product_uom_qty:
                line.state_commande = 'L'

            # 4- Si un mouvement de stock avec 'picking_type_code': 'incoming' est présent et qty_delivered = 0, État de la commande = R : réceptionné
            elif line.qty_delivered == 0:
                incoming_picking = order.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == 'incoming' and p.partner_id.id == order.partner_id.id)
                if incoming_picking:
                    line.state_commande = 'R'

            # Si aucune condition n'est remplie, mettre à jour en conséquence (facultatif)
            else:
                line.state_commande = False

            stock_move = self.env['stock.move'].search([
                ('picking_id.origin', '=', line.order_id.name),
                ('state', '!=', 'cancel'),  # On exclut les mouvements annulés
                ('picking_id.picking_type_code', '=', 'outgoing'),
            ], limit=1)
            

            # Si un mouvement de stock est trouvé, on obtient le picking correspondant
            if stock_move:
                line.id_bl = stock_move.picking_id
            else:
                line.id_bl = False

    liv_restant = fields.Float("% restant", compute="_compute_liv_restant")

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_liv_restant(self):
        for rec in self:
            if rec.qty_delivered == 0:
                rec.liv_restant = 0
            elif rec.qty_delivered < rec.product_uom_qty:
                rec.liv_restant = rec.qty_delivered / rec.product_uom_qty
            elif rec.qty_delivered == rec.product_uom_qty:
                rec.liv_restant = 100

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
        

        match = re.search(r'NewId_(\d+)', str(order_id))
        

        if match:
            order_id_number = int(match.group(1))
           
        else:
           
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


    @api.depends('order_id', 'sequence')
    def _compute_sequence_order(self):
        for order in self.mapped('order_id'):
            sequence = 1
            for line in order.order_line.sorted('sequence'):
                if line.product_id.product_tmpl_id.type_frais:  # Skip lines with type_frais
                    continue
                line.sequence_order = sequence
                sequence += 1
                

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

    frais_id = fields.Many2many(
        comodel_name='account.tax',
        relation='sale_order_line_frais_rel',  # Utilisation d'une table de relation différente
        string="Frais",
        compute='_compute_frais_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    tx_id = fields.Many2many(
        comodel_name='account.tax',
        relation='sale_order_line_tax_rel',  # Utilisation d'une table de relation différente
        string="Taxes",
        compute='_compute_tx_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    @api.depends('product_id', 'company_id')
    def _compute_frais_id(self):
        for line in self:
            frais_taxes = self.env['account.tax']
            if line.product_id:
                for frais_tax in line.product_id.frais:
                    frais_taxes |= frais_tax
            line.frais_id = frais_taxes

    @api.depends('product_id', 'company_id')
    def _compute_tx_id(self):
        for line in self:
            product_taxes = self.env['account.tax']
            if line.product_id:
                for tax in line.product_id.taxes_id:
                    product_taxes |= tax
            line.tx_id = product_taxes

    @api.depends('product_id', 'company_id', 'frais_id', 'tx_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['sale.order.line'])
        cached_taxes = {}

        for line in self:
            lines_by_company[line.company_id] += line

        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = line.frais_id | line.tx_id
                taxes_by_product_company[(line.product_id, company)] = taxes
                if not line.product_id or not taxes:
                    line.tax_id = False
                    continue

                fiscal_position = line.order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result

                line.tax_id = result

    # tax_id = fields.Many2many(
    #     comodel_name='account.tax',
    #     string="Taxes",
    #     compute='_compute_tax_id',
    #     store=True, readonly=False, precompute=True,
    #     context={'active_test': False},
    #     check_company=True)
    #
    # @api.depends('product_id', 'company_id')
    # def _compute_tax_id(self):
    #     taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
    #     lines_by_company = defaultdict(lambda: self.env['sale.order.line'])
    #     cached_taxes = {}
    #     for line in self:
    #         lines_by_company[line.company_id] += line
    #     for product in self.product_id:
    #         for tax in product.taxes_id:
    #             taxes_by_product_company[(product, tax.company_id)] += tax
    #         for frais_tax in product.frais:
    #             taxes_by_product_company[(product, frais_tax.company_id)] += frais_tax
    #     for company, lines in lines_by_company.items():
    #         for line in lines.with_company(company):
    #             taxes = taxes_by_product_company[(line.product_id, company)]
    #             if not line.product_id or not taxes:
    #                 # Nothing to map
    #                 line.tax_id = False
    #                 continue
    #             fiscal_position = line.order_id.fiscal_position_id
    #             cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
    #             if cache_key in cached_taxes:
    #                 result = cached_taxes[cache_key]
    #             else:
    #                 result = fiscal_position.map_tax(taxes)
    #                 cached_taxes[cache_key] = result
    #             # If company_id is set, always filter taxes by the company
    #             line.tax_id = result

class SaleOrder(models.Model):
    _inherit = "sale.order"

    interlocuteur = fields.Many2one('res.partner', string="Interlocuteur")
    contact_supply = fields.Many2one('res.partner', string="Contact Supply", related="partner_id.contact_supply")
    poids_carbone_unit = fields.Float("Poids Carbone unitaire", default=lambda self: self.env.company.poids_carbone.poids_carbone)
    poids_carbone_total = fields.Float("Poids Carbone Total", compute="_compute_poids_carbone_total")
    n_quality = fields.Char("Qualité", related="company_id.n_quality")
    current_user_id = fields.Many2one('res.users', string='Current User', compute='_compute_current_user_id',
                                      store=True)
    current_user_id_int = fields.Integer("id user")
    commande = fields.Boolean("Commande", default=False)

    @api.depends('order_line')
    def _compute_current_user_id(self):
        for order in self:
            order.current_user_id = self.env.user
            order.current_user_id = self.env.user.id
            if order.commande:
                order.state = "commande_recue"
           

    # user_id = fields.Many2one(
    #     comodel_name='res.users',
    #     string="Salesperson",
    #     compute='_compute_user_id',
    #     store=True, readonly=False, precompute=True, index=True,
    #     tracking=2,
    #     domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
    #         self.env.ref("sales_team.group_sale_salesman").id
    #     ))

    # @api.depends('create_uid')
    # def _compute_current_user(self):
    #     for order in self:
    #         order.current_user_id = self.env.user
  

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
            ('commande_recue', 'NON TRAITEES'),
            ('sale', "Bon de commande"),
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




    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_poids_carbone_total(self):
        for order in self:
            total_quantity = sum(
                line.product_uom_qty for line in order.order_line if line.product_id.fabrique == True)
            order.poids_carbone_total = total_quantity * order.poids_carbone_unit
            
            # order.current_user_id = self.env.user
            


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
        # print("template_id",template_id)
        for order in self:
            email_from = order.company_id.email
            email_to = order.partner_id.email
            menu_id = self.env.ref('sale.menu_sale_quotations').id
            action_id = self.env.ref('sale.action_quotations_with_onboarding').id
            so_url = self._make_url(self.id, self._name, menu_id, action_id)

            if email_from and email_to:
                # print(f"Sending email from {email_from} to {email_to} for order {order.name}")
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
            #else:
                # print(f"Email not sent for order {order.name}. Missing email_from or email_to.")

    @api.model
    def _cron_send_reminder_email(self):
        j_30 = (fields.Date.today() + relativedelta(days=30)).strftime('%Y-%m-%d')
        orders = self.search([('validity_date', '=', j_30)])
        # print(f"Orders found with validity_date = {j_30}: {orders}")
        for order in orders:
            order.send_reminder_email()
            # print("order.send_reminder_email()",order.send_reminder_email())

    def apply_threshold(self):
        for line in self.order_line:
            if line.price_subtotal < self.partner_id.seuil_a_la_ligne:
                line.price_subtotal = self.partner_id.seuil_a_la_ligne
                # print("line.frais_amount",line.frais_amount)

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
            # print("Triggering _compute_partner_invoice_id")
            if order.partner_id:
                # print("Partner found: ", order.partner_id.name)
                default_invoice_address = self.env['res.partner'].search([
                    ('parent_id', '=', order.partner_id.id),
                    ('address_facturation_par_defaut', '=', True)
                ], limit=1)

                if default_invoice_address:
                    # print("Default invoice address found: ", default_invoice_address.name)
                    order.partner_invoice_id = default_invoice_address
                else:
                    # print("No default invoice address found, using default Odoo address")
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

            # Créer ou récupérer un procurement group pour la commande de vente
            procurement_group = self.env['procurement.group'].search([
                ('sale_id', '=', order.id),
            ], limit=1)
            if not procurement_group:
                procurement_group = self.env['procurement.group'].create({
                    'name': order.name,
                    'sale_id': order.id,
                })

            # Créer un picking (bon d'entrée) pour chaque ligne valide
            picking = None
            for line in order.order_line:
                if (line.product_template_id.emplacement_produit_recu_client and
                        line.product_template_id.emplacement_produit_recu_client_qy and
                        line.product_id.product_tmpl_id.produit_recu_client and line.bon_reception == True):
                    # Créer le picking (bon d'entrée) pour cette ligne
                    picking_vals = {
                        'partner_id': order.partner_id.id,
                        'fiche_control_reception': True,
                        'picking_type_id': picking_type.id,  # Utiliser le picking_type de réception
                        'location_id': line.product_template_id.emplacement_produit_recu_client.id,
                        'produit_a_fabrique': line.product_template_id.id,
                        # Emplacement 'Entrée' comme source
                        'location_dest_id': line.product_template_id.emplacement_produit_recu_client_qy.id,
                        # Emplacement 'Stock' comme destination
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

                    # Créer les mouvements de stock pour cette ligne de commande
                    move_vals = {
                        'name': line.name,
                        'product_id': line.product_id.product_tmpl_id.produit_recu_client.product_variant_id.id,
                        'product_uom_qty': line.product_uom_qty,  # Ajouter la quantité
                        'product_uom': line.product_uom.id,
                        'delivery_date': line.date_livraison if not line.date_recale else line.date_recale,
                        'picking_id': picking.id,
                        'location_id': line.product_template_id.emplacement_produit_recu_client.id,
                        'location_dest_id': line.product_template_id.emplacement_produit_recu_client_qy.id,
                        'company_id': company.id,
                        'state': 'draft',
                        'group_id': procurement_group.id,
                        'sale_line_id': line.id,
                    }
                    stock_move = self.env['stock.move'].create(move_vals)
                    stock_move_line_vals = {
                        'move_id': stock_move.id,
                        'product_id': line.product_id.product_tmpl_id.produit_recu_client.product_variant_id.id,
                        'qty_done': line.product_uom_qty,  # qty_done égale à product_uom_qty
                        'product_uom_id': line.product_id.product_tmpl_id.produit_recu_client.product_variant_id.uom_id.id,
                        'location_id': line.product_template_id.emplacement_produit_recu_client.id,
                        'location_dest_id': line.product_template_id.emplacement_produit_recu_client_qy.id,
                        'company_id': company.id,
                    }
                    self.env['stock.move.line'].create(stock_move_line_vals)

            # Retourner l'action pour ouvrir la vue du dernier picking créé
            if picking:
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

