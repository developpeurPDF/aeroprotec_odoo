
from odoo import api, fields, models, _
from datetime import date, datetime, time

class StockMove(models.Model):
    _inherit = 'stock.move'

    is_conforme = fields.Selection([('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')], string="Conformité", readonly=True)
    quality_control_id = fields.Many2one('quality.control', string="Contrôle Qualité", readonly=True)

    quality_control_done = fields.Boolean(string="Quality Control Done", default=False)

    def action_open_quality_control(self):
        """Open the quality control record linked to this stock move"""
        self.ensure_one()
        if self.quality_control_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contrôle Qualité',
                'view_mode': 'form',
                'res_model': 'quality.control',
                'res_id': self.quality_control_id.id,
                'target': 'new',
            }

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    @api.onchange('sale_id')
    def get_origin(self):
        if self.sale_id:
            self.origin = str(self.sale_id.name)


    fiche_control_reception = fields.Boolean("Créer fiche Contrôle réception", default=False, store=True)
    bl_to_fact = fields.Boolean(string="1 BL = 1 Facture", store=True, related="partner_id.bl_to_fact")
    xfact_to_bl = fields.Boolean(string="X BL = 1 Facture", store=True, related="partner_id.xfact_to_bl")
    produit_a_fabrique = fields.Many2one("product.template",string="Produit à fabriquer")

    sale_id = fields.Many2one(related="group_id.sale_id", string="Sales Order", store=True, readonly=False,
                              index='btree_not_null', domain="[('partner_id', '=', partner_id)]")
    
    # supply_chain = fields.Many2one('res.users',string="Supplu Chain", store=True)
    # - un contrôle en réception sur quantité reçue / quantité bon commande client + état des pièces bon ou mauvais + remarques

    n_commande_client = fields.Char(string="Réf commande client")
    # contrôle reception

    date_controle_reception = fields.Date("Date de contrôle reception", readonly=True)
    controle_reception_traite_par = fields.Many2one('res.users', string="Traité par", readonly=True)

    date_deblocage = fields.Date("Date Déblocage", readonly=True)
    debloqe_par = fields.Many2one('res.users', string="Débloqué par", readonly=True)


    quantite = fields.Float(string="Quantité dans le bon de commande")#, compute="get_quantite"
    value_quantite = fields.Float(string="Quantité reçue", tracking=True)
    state_quantite = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme", compute="compute_state_quantite")
    label_state_quantite = fields.Char("Label statut quantité", compute="compute_label_state_quantite")

    def compute_label_state_quantite(self):
        for rec in self:
            if rec.state_quantite == "oui":
                rec.label_state_quantite = "Accepté"
            else:
                rec.label_state_quantite = "Non accepté"


    etat_piece = fields.Selection([('bon', 'Bon'), ('Mauvais', 'Mauvais')], string="Etat Pièce", default='bon', readonly=True)
    value_etat_piece = fields.Selection([('bon', 'Bon'), ('Mauvais', 'Mauvais')], string="Etat pièce reçu", tracking=True)
    state_etat_piece = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme", compute="compute_state_etat_piece")
    photo_etat_piece = fields.Binary(string="Photo de l'état de la pièce", tracking=True)

    remarque_controle_reception = fields.Text("Remarque Réception des pièces", tracking=True)

    conforme_controle_reception = fields.Selection([('conforme', 'Oui'), ('non_conforme', 'Non')],
                                string="Conformité du produit reçu",
                                compute="compute_conformite_reception",
                                store=True)

    def get_conforme_controle_reception_label(self):
        """Retourne l'étiquette (label) du champ conforme_controle_reception"""
        for record in self:
            if record.conforme_controle_reception == 'conforme':
                record.conforme_controle_reception_label = "Accepté"
            else:
                record.conforme_controle_reception_label = "Non Accepté"


    conforme_controle_reception_label = fields.Char(
        string="Conformité selon Contrôle reception (Label)",
        compute="get_conforme_controle_reception_label",)

    controle_reception_effectuer = fields.Boolean("Contrôle réception effectué", default=False, store=True, tracking=True)
    block = fields.Boolean("Bloquer la réception", default=False, store=True, tracking=True)

    def action_confirm_reception(self):
        self.ensure_one()  # Assure que self contient exactement un enregistrement
        self.write({
            'controle_reception_effectuer': True,
            'controle_reception_traite_par': self.env.user.id,
            'date_controle_reception': date.today()
        })

    def action_unlock(self):
        self.ensure_one()  # Assure que self contient exactement un enregistrement
        self.write({
            'block': False,
            'debloqe_par': self.env.user.id,
            'date_deblocage': date.today()
        })

    @api.depends('state_quantite', 'state_etat_piece')
    def compute_conformite_reception(self):
        for rec in self:
            if (rec.state_quantite == "oui" and rec.state_etat_piece == "oui"):
                rec.conforme_controle_reception = 'conforme'
                rec.block = False
            else:
                rec.conforme_controle_reception = 'non_conforme'
                rec.block = True

    @api.depends('move_ids_without_package')
    def get_quantite(self):
        for rec in self:
            move_ids = rec.move_ids_without_package
            # print("move_ids",move_ids)
            if len(move_ids) > 0:
                # print("len(move_ids) > 0")
                product = move_ids[0]
                if product:
                    rec.quantite = product.sale_line_id.product_uom_qty
                else:
                    rec.quantite = 1
            else:
                rec.quantite = 1


    @api.depends('quantite','value_quantite')
    def compute_state_quantite(self):
        for rec in self:
            if rec.quantite == rec.value_quantite:
                rec.state_quantite = "oui"
            else:
                rec.state_quantite = "non"

    @api.depends('etat_piece', 'value_etat_piece')
    def compute_state_etat_piece(self):
        for rec in self:
            if rec.etat_piece == rec.value_etat_piece:
                rec.state_etat_piece = "oui"
            else:
                rec.state_etat_piece = "non"

    # contrôle supply

    date_controle_supply = fields.Date("Date de contrôle supply" , readonly=True)
    controle_supply_traite_par = fields.Many2one('res.users', string="Traité par SC", readonly=True)

    prix = fields.Float(string="Prix",  readonly=True, related="produit_a_fabrique.list_price")
    value_prix = fields.Float(string="Prix reçu")
    state_prix = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme", compute="compute_state_prix")
    label_state_prix = fields.Char("Label statut prix", compute="compute_label_state_prix")

    def compute_label_state_prix(self):
        for rec in self:
            if rec.state_prix == "oui":
                rec.label_state_prix = "Accepté"
            else:
                rec.label_state_prix = "Non accepté"

    delai = fields.Float(string="Délai dans le bon de commande", compute="get_delai")
    n_of = fields.Char(string="N° OF", compute="_compute_n_of")

    @api.depends('n_of','produit_a_fabrique')
    def _compute_n_of(self):
        for picking in self:
            # Obtenir l'ID du produit à fabriquer à partir du modèle `product.template`
            product_id = self.env['product.product'].search([
                ('product_tmpl_id', '=', picking.produit_a_fabrique.id)
            ], limit=1)

            # Chercher l'ordre de fabrication lié
            production = self.env['mrp.production'].search([
                ('origin', '=', picking.origin),
                ('product_id', '=', product_id.id)
            ], limit=1)

            # Si trouvé, affecter le nom de l'ordre de fabrication au champ n_of
            picking.n_of = production.name if production else ''

            # Chercher les lignes de commande associées à la commande de vente
            sale_order_line = self.env['sale.order.line'].search([
                ('order_id', '=', picking.sale_id.id),
                ('product_id.product_tmpl_id', '=', picking.produit_a_fabrique.id)
            ], limit=1)

            # Si une ligne de commande correspondante est trouvée, mettre à jour la date recalée
            picking.date_recale = sale_order_line.date_recale if sale_order_line else False

    date_recale = fields.Date(string="Date recalée", compute='_compute_n_of', store=True)


    state_delai = fields.Selection([('oui', 'Oui'), ('non', 'Non'), ('litige', 'Litige')], string="Délai supply validé")#, compute="compute_state_delai")
    label_state_delai = fields.Char("Label statut prix", compute="compute_label_state_delai")

    def compute_label_state_delai(self):
        for rec in self:
            if rec.state_delai == "oui":
                rec.label_state_delai = "Accepté"
            else:
                rec.label_state_delai = "Non accepté"


    date_livraison_aero = fields.Datetime("Date de livraison estimée", compute="_compute_delivery_date")
    date_livraison_client = fields.Datetime("Date de livraison demandée par le client", tracking=True)
    state_date_livraison_client = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme", compute="compute_state_date_livraison_client")

    remarque_controle_supply = fields.Text("Remarque Contrôle de la supply", tracking=True)

    conforme_controle_supply = fields.Selection(
        [('conforme', 'Oui'), ('non_conforme', 'Non')],
        string="Conformité selon Contrôle de la supply ",
        compute="compute_conformite_supply",
        store=True)

    def get_conforme_controle_supply_label(self):
        for record in self:
            if record.conforme_controle_supply_label == 'conforme':
                record.conforme_controle_supply_label = "Accepté"
            else:
                record.conforme_controle_supply_label = "Non Accepté"

    conforme_controle_supply_label = fields.Char(
        string="Conformité selon Contrôle de la supply (Label)",
        compute="get_conforme_controle_supply_label",
    )

    controle_supply_effectuer = fields.Boolean("Contrôle supply effectué", default=False, tracking=True)

    def action_confirm_cq_supply(self):
        self.ensure_one()  # Assure que self contient exactement un enregistrement
        self.write({
            'controle_supply_effectuer': True,
            'controle_supply_traite_par': self.env.user.id,
            'date_controle_supply': date.today(),
        })




    @api.depends('move_ids_without_package')
    def get_delai(self):
        for rec in self:
            move_ids = rec.move_ids_without_package
            if move_ids:  # Vérifie que move_ids n'est pas vide
                product = move_ids[0]
                if product and product.sale_line_id:  # Vérifie que product et sale_line_id existent
                    if product.sale_line_id.days_to_prepare_mo:
                        # Additionner le delai en fonction de la valeur existante
                        if product.sale_line_id.sale_delay:
                            rec.delai = product.sale_line_id.days_to_prepare_mo + product.sale_line_id.sale_delay
                            # print("self.delai:1", rec.delai)
                        elif product.sale_line_id.produce_delay:
                            rec.delai = product.sale_line_id.days_to_prepare_mo + product.sale_line_id.produce_delay
                        #     print("self.delai:2", rec.delai)
                        # print("self.delai:", rec.delai)
                    else:
                        rec.delai = 0  # Si days_to_prepare_mo n'existe pas, initialise delai à 0
                else:
                    rec.delai = 0  # Si product ou sale_line_id n'existe pas, initialise delai à 0
            else:
                rec.delai = 0  # Si move_ids est vide, initialise delai à 0

    @api.depends('move_ids_without_package')
    def _compute_delivery_date(self):
        for rec in self:
            move_ids = rec.move_ids_without_package
            if move_ids:
                move_line = move_ids[0]  # On récupère la première ligne de mouvement
                if move_line:
                    sale_line = move_line.sale_line_id
                    if sale_line:
                        # Calculer la date de livraison en utilisant les attributs du bon modèle
                        # delivery_date = sale_line.order_id.date_order
                        delivery_date = sale_line.delivery_dates
                        if delivery_date and sale_line.sale_delay:
                            final_date = rec.env['sale.order.line']._calculate_final_date(
                                delivery_date,
                                (sale_line.sale_delay + sale_line.days_to_prepare_mo)
                            )
                            rec.date_livraison_aero = final_date
                        elif delivery_date and sale_line.produce_delay:
                            final_date = rec.env['sale.order.line']._calculate_final_date(
                                delivery_date,
                                (sale_line.days_to_prepare_mo + sale_line.produce_delay)
                            )
                            rec.date_livraison_aero = final_date
                        else:
                            rec.date_livraison_aero = rec.date_deadline
                    else:
                        rec.date_livraison_aero = rec.date_deadline
                else:
                    rec.date_livraison_aero = rec.date_deadline
            else:
                rec.date_livraison_aero = rec.date_deadline

    @api.depends('state_delai', 'state_prix')
    def compute_conformite_supply(self):
        for rec in self:
            if (rec.state_delai == "oui" and rec.state_prix == "oui" and rec.state_date_livraison_client == "oui"):
                rec.conforme_controle_supply = 'conforme'
            else:
                rec.conforme_controle_supply = 'non_conforme'

    @api.depends('prix', 'value_prix')
    def compute_state_prix(self):
        for rec in self:
            if rec.prix == rec.value_prix:
                rec.state_prix = "oui"
            else:
                rec.state_prix = "non"

    # @api.depends('delai', 'value_delai')
    # def compute_state_delai(self):
    #     for rec in self:
    #         if rec.delai == rec.value_delai:
    #             rec.state_delai = "oui"
    #         else:
    #             rec.state_delai = "non"

    @api.depends('date_livraison_aero', 'date_livraison_client')
    def compute_state_date_livraison_client(self):
        for rec in self:
            date_livraison_aero = rec.date_livraison_aero
            date_livraison_client = rec.date_livraison_client

            if isinstance(date_livraison_aero, datetime) and isinstance(date_livraison_client, datetime):
                if date_livraison_aero <= date_livraison_client:
                    rec.state_date_livraison_client = 'oui'
                else:
                    rec.state_date_livraison_client = 'non'
            else:
                # Traiter le cas où l'une des valeurs n'est pas une date
                rec.state_date_livraison_client = 'non'  # Ou définissez une autre valeur par défaut appropriée

    # contrôle Méthode
    date_controle_methode = fields.Date("Date de contrôle Méthode", readonly=True)
    controle_methode_traite_par = fields.Many2one('res.users', string="Traité par MQ", readonly=True)

    ref_methode = fields.Char(string="Référence méthode")
    changement_indice = fields.Char(string="Indice Gamme", compute="get_indice")
    value_changement_indice = fields.Char(string="Indice Gamme reçu", tracking=True)
    state_changement_indice = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme", compute="compute_state_changement_indice")

    changement_traitement = fields.Char(string="Référence Gamme", compute="get_changement_traitement")


    code_opr = fields.Char(string="Codes des opérations", compute="get_code_opr")


    norme_indice_interne = fields.Char(string="Norme interne et indice", compute="get_norme_indice_interne")


    norme_indice_externe = fields.Char(string="Norme externe et indice", compute="get_norme_indice_externe")


    ecart = fields.Char(string="Ecart demande client et gamme", tracking=True)
    # value_ecart = fields.Char(string="Ecart demande client et gamme")
    state_ecart = fields.Selection([('oui', 'Accepté'), ('non', 'Non accepté'), ('litige', 'Litige')], string="Statut contrôle Méthode", tracking=True)

    remarque_controle_methode = fields.Text("Remarque Méthode", tracking=True)

    conforme_controle_methode = fields.Selection(
        [('conforme', 'Oui'), ('non_conforme', 'Non')],
        string="Conformité selon contrôle méthode",
        compute="compute_conformite_methode",
        store=True)

    def get_conforme_controle_methode_label(self):
        """Retourne l'étiquette (label) du champ conforme_controle_methode"""
        for record in self:
            if record.conforme_controle_methode_label == 'conforme':
                record.conforme_controle_methode_label = "Accepté"
            else:
                record.conforme_controle_methode_label = "Non Accepté"

    conforme_controle_methode_label = fields.Char(
        string="Conformité selon Contrôle methode (Label)",
        compute="get_conforme_controle_methode_label",)

    controle_methode_effectuer = fields.Boolean("Contrôle méthode effectué", default=False, tracking=True)

    def action_confirm_cq_methode(self):
        self.ensure_one()  # Assure que self contient exactement un enregistrement
        self.write({
            'controle_methode_effectuer': True,
            'controle_methode_traite_par': self.env.user.id,
            'date_controle_methode': date.today()
        })

    @api.depends('move_ids_without_package')
    def get_indice(self):
        for rec in self:
            rec.changement_indice = "---"
            move_ids = rec.move_ids_without_package
            if move_ids:  # Vérifie que move_ids n'est pas vide
                product = move_ids[0]
                if product and product.sale_line_id.product_template_id:  # Vérifie que product et sale_line_id existent
                    if product.sale_line_id.product_template_id.indice:
                        rec.changement_indice = product.sale_line_id.product_template_id.indice

    @api.depends('move_ids_without_package')
    def get_changement_traitement(self):
        for rec in self:
            # Initialiser la valeur par défaut
            rec.changement_traitement = "---"

            # move_ids = rec.move_ids_without_package
            if rec.produit_a_fabrique:

                if rec.produit_a_fabrique.bom_ids:
                    if rec.produit_a_fabrique.bom_ids.code:
                        rec.changement_traitement = rec.produit_a_fabrique.bom_ids[0].code

    first_bom_operation_ids = fields.One2many(
        'mrp.routing.workcenter',
        string="Opérations",
        compute='_compute_first_bom_operations'
    )

    @api.depends('move_ids_without_package')
    def _compute_first_bom_operations(self):
        for rec in self:
            # Initialiser la valeur par défaut
            rec.first_bom_operation_ids = None

            if rec.produit_a_fabrique:

                if rec.produit_a_fabrique.bom_ids:
                    if rec.produit_a_fabrique.first_bom_operation_ids:
                        rec.first_bom_operation_ids = rec.produit_a_fabrique.first_bom_operation_ids


    @api.depends('move_ids_without_package')
    def get_code_opr(self):
        for rec in self:
            # Initialiser la valeur par défaut
            rec.code_opr = "---"

            if rec.produit_a_fabrique:

                if rec.produit_a_fabrique.bom_ids:
                    if rec.produit_a_fabrique.bom_ids.code_opr:
                        rec.code_opr = rec.produit_a_fabrique.bom_ids[0].code_opr

    @api.depends('move_ids_without_package')
    def get_norme_indice_interne(self):
        for rec in self:
            # Initialiser la valeur par défaut
            rec.norme_indice_interne = "---"

            if rec.produit_a_fabrique:
                if rec.produit_a_fabrique.bom_ids:
                    if rec.produit_a_fabrique.bom_ids.norme_interne:
                        rec.norme_indice_interne = rec.produit_a_fabrique.bom_ids[0].norme_interne

    @api.depends('move_ids_without_package')
    def get_norme_indice_externe(self):
        for rec in self:
            # Initialiser la valeur par défaut
            rec.norme_indice_externe = "---"

            if rec.produit_a_fabrique:

                if rec.produit_a_fabrique.bom_ids:
                    if rec.produit_a_fabrique.bom_ids.norme_externe:
                        rec.norme_indice_externe = rec.produit_a_fabrique.bom_ids[0].norme_externe



    @api.depends('state_changement_indice','state_ecart')
    def compute_conformite_methode(self):
        for rec in self:
            if rec.state_ecart == "oui" and rec.state_changement_indice =="oui":
                rec.conforme_controle_methode = 'conforme'
            else:
                rec.conforme_controle_methode = 'non_conforme'

    @api.depends('changement_indice', 'value_changement_indice')
    def compute_state_changement_indice(self):
        for rec in self:
            if rec.changement_indice == rec.value_changement_indice:
                rec.state_changement_indice = "oui"
            else:
                rec.state_changement_indice = "non"

    date_livraison_aero_only_date = fields.Date("Date de livraison estimée (sans heure)",
                                                compute="_compute_delivery_date_only")

    def _compute_delivery_date_only(self):
        for record in self:
            if record.date_livraison_aero:
                record.date_livraison_aero_only_date = record.date_livraison_aero.date()
            else:
                record.date_livraison_aero_only_date = False

    date_livraison_client_date = fields.Date("Date de livraison demandée (sans heure)",
                                                compute="_compute_delivery_client_date_only")

    def _compute_delivery_client_date_only(self):
        for record in self:
            if record.date_livraison_client:
                record.date_livraison_client_date = record.date_livraison_aero.date()


    def _get_first_move_qty(self):
        for record in self:
            if record.move_ids_without_package:
                # Assurez-vous que move_ids_without_package est trié si nécessaire
                first_move = record.move_ids_without_package[0]
                record.first_move_qty = first_move.product_uom_qty
            else:
                record.first_move_qty = 0.0

    first_move_qty = fields.Float(
        string='First Move Quantity',
        compute='_get_first_move_qty',
        store=True
    )



