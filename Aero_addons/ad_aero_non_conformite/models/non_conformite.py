from odoo import models, fields, api

class NonConformite(models.Model):
    _name = 'non.conformite'
    _description = 'Gestion des Non-Conformités'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default='Nouveau', tracking=True)
    quality_checks_id = fields.Many2one(
        comodel_name='quality.checks',
        string="Contrôle",
        required=True, ondelete='cascade', index=True, copy=False)
    produit = fields.Many2one('product.product', string='Produit', tracking=True)
    client = fields.Many2one('res.partner', string='Client', tracking=True)
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
    of_reprise = fields.Many2one('mrp.production', string='OF reprise', tracking=True)
    raison_sociale_client = fields.Char(string='Raison sociale du client', tracking=True)
    ref_commande_client = fields.Char(string='Référence client de la commande', tracking=True)
    reference_article = fields.Char(string='Référence de l’article', compute='_compute_reference_article', tracking=True)

    @api.depends('produit')
    def _compute_reference_article(self):
        for record in self:
            record.reference_article = record.produit.default_code if record.produit else ''
    designation_article = fields.Char(
        string='Désignation de l’article', tracking=True
    )
    quantite_initiale_of = fields.Integer(string='Quantité initiale de l’OF', tracking=True)
    quantite_nc = fields.Integer(string='Quantité non conforme déclarée', tracking=True)
    date_creation_nc = fields.Datetime(
        string='Date de création de la NC', default=fields.Datetime.now, tracking=True
    )
    utilisateur_creation_nc = fields.Many2one(
        'res.users', string='Utilisateur ayant créé la NC', default=lambda self: self.env.user, tracking=True
    )
    ilot_machine_responsable = fields.Many2one('mrp.workcenter', string='Ilot ou/et machine responsable de la NC', tracking=True)
    type_defaut = fields.Many2one('type.defaut', string="Type de Défaut", tracking=True)

    description_defaut = fields.Char(string="Renseigner la description du défaut", tracking=True)

    causes_non_conformite = fields.Many2one(
        'cause.non.conformite',
        string="Causes de la Non-Conformité", tracking=True
    )

    cause_detail = fields.Char(string="Renseigner un champ pour précise la cause", tracking=True)

    decision = fields.Selection([
        ('accepted', "Accepté en l'état"),
        ('derogation', 'Dérogation'),
        ('reworked', 'Repris par Aeroprotec'),
    ], string="Décision", tracking=True, default='accepted')

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
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)

    def action_generate_of_reprise(self):
        for record in self:
            new_of = self.env['mrp.production'].create({
                # 'name': f"OF - {record.name}",
                'product_id': record.produit.id,
                'product_qty': 1.0,
                'product_uom_id': record.produit.uom_id.id,

            })
            self.of_reprise = new_of.id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'res_id': new_of.id,
                'target': 'current',
            }

    #plan d'action
    type_action = fields.Selection(
        selection=[
            ('amelioration', 'Amélioration'),
            ('preventive', 'Préventive'),
            ('corrective', 'Corrective'),
        ],
        string="Type d’action", tracking=True
    )
    descriptif_action = fields.Text(string="Descriptif de l'action", tracking=True)
    date_creation_action = fields.Datetime(string="Date de création de l'action", default=fields.Datetime.now, tracking=True)
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
    lot = fields.Many2one('stock.lot', string="LOT", tracking=True)

    #Séquence
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('non.conformite') or 'Nouveau'
        return super(NonConformite, self).create(vals)

    # les status
    state = fields.Selection(
        [
            ('declarer', 'Déclaré'),
            ('acceptee_etat', "Acceptée en l'état"),
            ('acceptee_retouche', 'Acceptée sous reserve de retouche'),
            ('encours_remise', 'En cours de remise en conformité'),
            ('encours', 'En cours'),
            ('cloturee', 'Clôturée')
        ],
        string="State",
        default='declarer'
    )

    def action_accept_state(self):
        self.state = 'acceptee_etat'


    def action_accept_retouche(self):
        self.state = 'acceptee_retouche'

    def action_encours_remise(self):
        self.state = 'encours_remise'

    def action_encours(self):
        self.state = 'encours'


    def action_close(self):
        self.state = 'cloturee'
