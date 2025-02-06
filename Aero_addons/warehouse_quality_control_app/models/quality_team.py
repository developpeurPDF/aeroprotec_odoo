# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class quality_team(models.Model):
    _name = "quality.team"
    _description = "Quality Team"

    name = fields.Char(string='Nom')
    alias_id = fields.Many2one('mail.alias',string="Email Alias",ondelete="restrict")
    alias_name = fields.Char('Email Alias')
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    employee_ids = fields.Many2many('hr.employee',string="Employeés")

class quality_alert(models.Model):
    _name = "quality.alert"
    _description = "Quality Alert"

    _inherit = ['mail.thread']

    name = fields.Char('Nom', readonly=True)
    title = fields.Char('Titre')
    #product_temp_id = fields.Many2one('product.template',string="Product")
    product_id = fields.Many2one('product.product',string="Produit")
    lot_id = fields.Many2one('stock.lot',string="LOT")

    user_id = fields.Many2one('res.users',string="Responsable")
    priority = fields.Selection([('n','normal'),('l','low'),('h','high'),('v','very_high')],string='Priorité',default='n')

    description = fields.Html(string="description")
    correct_actions = fields.Html(string="Correct Actions")
    preventive_actions = fields.Html(string="Preventive Actions")
    partner_id = fields.Many2one('res.partner',string="Fournisseur")
    date_assigned = fields.Datetime(string="Date d'attribution")
    date_close = fields.Datetime(string="Date de clôture")
    state_id = fields.Many2one('quality.alert.stage',string="State")
    tag_ids = fields.Many2many('quality.tags',string="Tags")
    picking_id = fields.Many2one('stock.picking',string="Picking")
    team_id = fields.Many2one('quality.team',string="Équipe")

    @api.model
    def default_get(self, fields):
        res  = super(quality_alert, self).default_get(fields)
        stage = self.env['quality.alert.stage'].search([],order="sequence", limit=1)
        if stage :
            res['state_id'] = stage.id
        return res

    @api.model
    def create(self, vals):    

        seq = self.env['ir.sequence'].next_by_code('quality.alert') or '/'
        vals['name'] = seq
        if self._context.get('picking_res') :
            vals['picking_id'] = int(self._context.get('picking_res'))
        return super(quality_alert, self).create(vals)

    #Gestion des non conformite clients

    source_nc = fields.Selection(
        selection=[
            ('production', 'Production'),
            ('laboratoire_installations', 'Laboratoire – Installations'),
            ('laboratoire_suivi_serie', 'Laboratoire – Suivi série'),
        ],
        string='Source de la NC', tracking=True
    )
    criticite = fields.Selection(
        selection=[
            ('mineure', 'Mineure'),
            ('majeure', 'Majeure'),
            ('critique', 'Critique'),
        ],
        string='Criticité', tracking=True
    )
    commande_initiale = fields.Many2one('sale.order', string='Commande initiale', tracking=True)
    of_initiale = fields.Many2one('mrp.production', string='OF initiale', tracking=True)
    of_reprise = fields.Many2one('mrp.production', string='OF reprise', tracking=True, compute="_compute_of_reprise")

    @api.depends('commande_reprise_client', 'commande_reprise_client.mrp_production_ids')
    def _compute_of_reprise(self):
        for record in self:
            if record.commande_reprise_client:

                mrp_production = record.commande_reprise_client.mrp_production_ids[:1]
                record.of_reprise = mrp_production
            else:
                record.of_reprise = False
    raison_sociale_client = fields.Char(string='Raison sociale du client', tracking=True)
    ref_commande_client = fields.Char(
        string='Référence client', tracking=True, compute='_compute_ref_commande_client'
    )
    @api.depends('commande_initiale_client')
    def _compute_ref_commande_client(self):
        for record in self:
            record.ref_commande_client = record.commande_initiale_client.client_order_ref or ''

    ref_commande_fournisseur = fields.Char(string='Référence fournisseur', compute="_compute_ref_commande_fournisseur", tracking=True)

    @api.depends('commande_initiale_fournisseur')
    def _compute_ref_commande_fournisseur(self):
        for record in self:
            record.ref_commande_fournisseur = record.commande_initiale_fournisseur.partner_ref or ''

    ligne_commande_client = fields.Many2one('sale.order.line', string='Ligne de commande', tracking=True, compute="_compute_ligne_commande_client")

    @api.depends('product_id', 'commande_initiale_client')
    def _compute_ligne_commande_client(self):
        for record in self:
            if record.product_id and record.commande_initiale_client:
                line = self.env['sale.order.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id', '=', record.commande_initiale_client.id)
                ], limit=1)
                record.ligne_commande_client = line.id
            else:
                record.ligne_commande_client = False

    ligne_commande_fournisseur = fields.Many2one('purchase.order.line', string='Ligne de commande', tracking=True, compute="_compute_ligne_commande_fournisseur")

    @api.depends('product_id', 'commande_initiale_fournisseur')
    def _compute_ligne_commande_fournisseur(self):
        for record in self:
            if record.product_id and record.commande_initiale_fournisseur:

                line = self.env['purchase.order.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id', '=', record.commande_initiale_fournisseur.id)
                ], limit=1)
                record.ligne_commande_fournisseur = line.id
            else:
                record.ligne_commande_fournisseur = False



    ref_commande_client_reprise = fields.Char(string='Référence client', compute="_compute_ref_commande_client_reprise", tracking=True)

    @api.depends('commande_reprise_client')
    def _compute_ref_commande_client_reprise(self):
        for record in self:
            record.ref_commande_client_reprise = record.commande_reprise_client.client_order_ref or ''

    ref_commande_fournisseur_reprise = fields.Char(string='Référence fournisseur', compute="_compute_ref_commande_fournisseur_reprise", tracking=True)

    @api.depends('commande_reprise_fournisseur')
    def _compute_ref_commande_fournisseur_reprise(self):
        for record in self:
            record.ref_commande_fournisseur_reprise = record.commande_reprise_fournisseur.partner_ref or ''

    ligne_commande_client_reprise = fields.Many2one('sale.order.line', string='Ligne de commande', tracking=True, compute="_compute_ligne_commande_client_reprise")

    @api.depends('product_id', 'commande_reprise_client')
    def _compute_ligne_commande_client_reprise(self):
        for record in self:
            if record.product_id and record.commande_reprise_client:
                line = self.env['sale.order.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id', '=', record.commande_reprise_client.id)
                ], limit=1)
                record.ligne_commande_client_reprise = line.id
            else:
                record.ligne_commande_client_reprise = False
    ligne_commande_fournisseur_reprise = fields.Many2one('purchase.order.line', string='Ligne de commande', tracking=True, compute="_compute_ligne_commande_fournisseur_reprise")

    @api.depends('product_id', 'commande_reprise_fournisseur')
    def _compute_ligne_commande_fournisseur_reprise(self):
        for record in self:
            if record.product_id and record.commande_reprise_fournisseur:

                line = self.env['purchase.order.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id', '=', record.commande_reprise_fournisseur.id)
                ], limit=1)
                record.ligne_commande_fournisseur_reprise = line.id
            else:
                record.ligne_commande_fournisseur_reprise = False

    reference_article = fields.Char(string='Référence de l’article', compute='_compute_reference_article',
                                    tracking=True)

    @api.depends('product_id')
    def _compute_reference_article(self):
        for record in self:
            record.reference_article = record.product_id.default_code if record.product_id else ''

    designation_article = fields.Char(
        string='Désignation de l’article', tracking=True
    )
    quantite_initiale_of = fields.Integer(string='Quantité initiale de l’OF', tracking=True)
    quantite_nc = fields.Integer(string='Quantité non conforme déclarée', tracking=True)
    date_creation_nc = fields.Datetime(
        string='Date de création de la NC', default=fields.Datetime.now, tracking=True
    )
    utilisateur_creation_nc = fields.Many2one(
        'res.users', string='Créateur', default=lambda self: self.env.user, tracking=True
    )
    ilot_machine_responsable = fields.Many2one('mrp.workcenter', string='Ilot ou/et machine responsable de la NC',
                                               tracking=True)
    defaut_id = fields.Many2many('type.defaut', string="Type de Défaut", tracking=True)

    description_defaut = fields.Char(string="Renseigner la description du défaut", tracking=True)
    site = fields.Char(string="Site", tracking=True)
    cause_non_destruction = fields.Char(string="Renseigner la cause de non destruction", tracking=True)

    nonconformite_id = fields.Many2many(
        'cause.non.conformite',
        string="Causes de la Non-Conformité", tracking=True
    )
    cause_non_detection = fields.Many2many(
        'cause.non.detection',
        string="Renseigner la ou les causes de la non détection", tracking=True
    )
    cause_occurence = fields.Many2many(
        'cause.occurrence',
        string="Renseigner la ou les causes d'occurrence et non détection", tracking=True
    )
    client = fields.Many2one('res.partner', string="Client")

    cause_detail = fields.Char(string="Renseigner un champ pour précise la cause", tracking=True)

    decision = fields.Selection([
        ('accepte_etat', "Accepté en l'état"),
        ('derogation', "Dérogation"),
        ('repris_aeroprotec', "Repris par Aeroprotec"),
        ('rebut_client', "Rebuté par le client"),
        ('non_reprenables', "Pièces non reprenables"),
        ('non_imputable', "Non-imputable à Aeroprotec"),
        ('repris_client', "Repris par client"),
    ], string="Décision")

    date_cloture = fields.Datetime(string="Date de Clôture", tracking=True)
    nc_sur_fai = fields.Char(string="NC sur FAI", tracking=True)
    gamme_reprise = fields.Many2one(
        'mrp.bom',
        string="Gamme de reprise", tracking=True
    )
    of = fields.Many2one(
        'mrp.production',
        string="OF", tracking=True
    )
    tiers = fields.Selection(
        [
            ('client', 'Client'),
            ('fournisseur', 'Fournisseur'),
            ('sous_traitant', 'Sous-traitant'),
        ],
        string="Tiers"
    )
    commande_initiale_client = fields.Many2one(
        'sale.order', string="Commande"
    )
    commande_initiale_fournisseur = fields.Many2one(
        'purchase.order', string="Commande"
    )
    commande_reprise_client = fields.Many2one(
        'sale.order', string="Commande"
    )
    commande_reprise_fournisseur = fields.Many2one(
        'purchase.order', string="Commande"
    )
    bl_client = fields.Many2one(
        'stock.picking',
        string="BL"
    )
    bl_fournisseur = fields.Many2one(
        'stock.picking',
        string="BL",

    )
    bl_client_reprise = fields.Many2one(
        'stock.picking',
        string="BL",
        domain="[('picking_type_id.code', '=', 'incoming'), ('sale_id', '=', commande_reprise_client)]"
    )
    bl_fournisseur_reprise = fields.Many2one(
        'stock.picking',
        string="BL",
        domain="[('picking_type_id.code', '=', 'incoming'), ('purchase_id', '=', commande_reprise_fournisseur)]"
    )
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)

    def action_generate_of_reprise(self):
        for record in self:

            new_of = self.env['mrp.production'].create({
                'name': f"OF - {record.name}",
                'product_id': record.product_id.id,
                'product_qty': 1.0,
                'product_uom_id': record.product_id.uom_id.id,


            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'res_id': new_of.id,
                'target': 'current',
            }

    def action_create_sale_order(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].create({'partner_id': self.client.id})
        if self.product_id:
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'product_uom_qty': 1.0,
                'price_unit': self.product_id.lst_price,
            })
        self.commande_reprise_client = sale_order.id
        #self.of_reprise = sale_order.mrp_production_ids.id
        return {
            'name': 'Bon de Commande',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
        }

    def action_create_purchase_order(self):
        self.ensure_one()
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.client.id,
        })
        if self.product_id:
            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'product_qty': 1.0,
                'price_unit': self.product_id.standard_price,
                'date_planned': fields.Date.today(),
            })
        self.commande_reprise_fournisseur = purchase_order.id
        return {
            'name': 'Bon de Commande Fournisseur',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': purchase_order.id,
            'target': 'current',
        }

    # plan d'action
    type_action = fields.Selection(
        selection=[
            ('amelioration', 'Amélioration'),
            ('preventive', 'Préventive'),
            ('corrective', 'Corrective'),
        ],
        string="Type d’action", tracking=True
    )
    descriptif_action = fields.Text(string="Descriptif de l'action", tracking=True)
    date_creation_action = fields.Datetime(string="Date de création de l'action", default=fields.Datetime.now,
                                           tracking=True)
    date_realisation_action = fields.Datetime(string="Date de réalisation de l'action", tracking=True)
    efficacite = fields.Selection(
        selection=[('oui', 'Oui'), ('non', 'Non')],
        string="Efficacité", tracking=True
    )

    action_cloturee = fields.Selection(
        selection=[('oui', 'Oui'), ('non', 'Non')], string="Action clôturée", tracking=True)
    validateur_action = fields.Many2one('res.users', string="Validateur de l'action", tracking=True)
    responsable_action_id = fields.Many2one(
        'res.users',
        string="Responsable de l'action",
        tracking=True
    )



class quality_alert_stage(models.Model):
    _name = "quality.alert.stage"
    _order = 'sequence'

    name = fields.Char('Nom')
    sequence = fields.Integer(string="Sequence")
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)

class quality_tags(models.Model) :
    _name = "quality.tags"

    name = fields.Char('Nom')

