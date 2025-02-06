# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Quality_point(models.Model):
    _inherit = 'quality.point'

    commentaire = fields.Text(string='Commentaire')
    matiere = fields.Many2one('matiere.parameter.value', string="Matière", tracking=True)

    operation_id = fields.Many2many('mrp.routing.workcenter', string="Centre d'opérations des bons de travail")
    # code_operation = fields.Char(related="operation_id.code_operation")
    code = fields.Selection(
        [('mrp_operation', 'Manufacturing Operation'), ('incoming', 'Vendors'), ('outgoing', 'Customers'),
         ('internal', 'Internal')], related="picking_type_id.code", string="Code")
    test_type = fields.Selection(
        [('pass_fail', 'Pass-Fail'), ('measure', 'Measure'), ('picture', 'Take a Picture'), ('text', 'Text')],
        string="Type", default='pass_fail')

    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True, )
    quantite_conforme = fields.Integer(string="Quantité conforme",)
    quantite_non_conforme = fields.Integer(string="Quantité non conforme",)

    # integrite_piece = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ],
    #                                   string="Intégrité des Pièces", )


    point_qualite = fields.Selection([('Après toutes les phases', 'Après toutes les phases'),
                                      ('Contrôle épaisseur', 'Contrôle épaisseur'),
                                      ('Création des mélanges de peinture', 'Création des mélanges de peinture'),
                                      ('Association des mélanges peintures', 'Association des mélanges peintures'),
                                      ],
                                      string="Point Qualité", )

    controle_epaisseur_ts_min = fields.Float("Contrôle épaisseur Min")
    controle_epaisseur_ts_max = fields.Float("Contrôle épaisseur Max")
    controle_epaisseur_ts_moyen = fields.Float("Contrôle épaisseur Moyen")

    adherence_ts = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ], string="Adhérence", )

    controle_epaisseur_peinture_min = fields.Float("Contrôle épaisseur Min")
    controle_epaisseur_peinture_max = fields.Float("Contrôle épaisseur Max")
    controle_epaisseur_peinture_moyen = fields.Float("Contrôle épaisseur Moyen")

    adherence_peinture = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ], string="Adhérence", )


    controle_polymerisation = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ], string="Contrôle de la polymérisation ", )
    continuite_couche = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ], string="Continuité de couche", )
    test_colmatage = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ], string="Test de colmatage", )
    continuite_electrique = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ], string="Continuité électrique", )

    controle_epaisseur_cf_min = fields.Float("Contrôle épaisseur Min")
    controle_epaisseur_cf_max = fields.Float("Contrôle épaisseur Max")
    controle_epaisseur_cf_moyen = fields.Float("Contrôle épaisseur Moyen")

    type_peinture = fields.Char("Type peinture")
    lot_base = fields.Char("Lot Base")
    lot_durcisseur = fields.Char("Lot Durcisseur")
    lot_diluant = fields.Char("Lot Diluant")
    temperature = fields.Char("Température")
    hygrometrie = fields.Char("Hygrométrie")
    viscosite = fields.Char("Viscosité")
    date_fabrication = fields.Date("Date de fabrication")

    type_article = fields.Selection(selection=[
        ('Production', 'Production'),
        ('Eprouvette', 'Eprouvette'),
        ('Composant', 'Composant'),
        ('Outillage', 'Outillage'),
    ],
        string="Type produit", )

    type_gamme = fields.Selection([
        ('production', 'GAMME DE PRODUCTION'),
        ('reprise', 'GAMME DE REPRISE'), ('epouvettes', 'GAMME DES ARTICLES EPOUVETTES')], "Type d'OF", )

    nom_controle = fields.Char(string="Nom du contrôle")

    @api.onchange('product_temp_id')
    def _onchange_product_temp_id(self):
        if self.product_temp_id:

            self.type_article = self.product_temp_id.type_article
            # self.type_gamme = self.product_temp_id.type_gamme
            self.matiere = self.product_temp_id.matiere
        else:

            self.type_article = False
            # self.type_gamme = False
            self.matiere = False







class Quality_check(models.Model):
    _inherit = 'quality.checks'





    # related="product_id.product_tmpl_id.type_article")
    nom_controle = fields.Char(string="Nom du contrôle")
    commentaire = fields.Text(string='Commentaire')

            # related="mrp_id.bom_id.type_gamme")

    quality_checks_line_id = fields.One2many(
        comodel_name='quality.checks.line',
        inverse_name='quality_checks_ids',
        string="Lignes du contrôle",
        copy=True, auto_join=True)

    quantite_conforme = fields.Integer(string="Quantité conforme", )
    quantite_non_conforme = fields.Integer(string="Quantité non conforme", )

    echantillon = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Échantillonnage", required=True)
    quantite_controle = fields.Integer(string="Quantité contrôlé")
    quantite_fabrique = fields.Integer(string="Quantité fabriquée", related="workorder_id.total_fabricated_qty")

    # @api.depends('quality_checks_line_id.quntite_controle')
    # def _compute_total_quantite_controle(self):
    #     for check in self:
    #         check.quantite_controle = sum(line.quntite_controle for line in check.quality_checks_line_id)

    # mrp_id = fields.Many2one('mrp.production', string="Production Name", related="workorder_id.production_id", store=True)
    # workorder_id = fields.Many2one('mrp.workorder', string="Work-order")
    workorder_id = fields.Many2one(
        'mrp.workorder', string="Workorder",
        help="The work order related to this quality check"
    )
    mrp_id = fields.Many2one(
        'mrp.production', string="Manufacturing Order",
        related="workorder_id.production_id", store=True,
        help="The manufacturing order related to this quality check"
    )
    picture = fields.Binary(string="Photo")
    test_type = fields.Selection(
        [('pass_fail', 'Pass-Fail'), ('measure', 'Measure'), ('picture', 'Take a Picture'), ('text', 'Text')],
        string="Type", default='pass_fail', related="quality_point_id.test_type")

    def validate_picture(self):
        self.write({'state': 'pass', 'date': fields.datetime.now().date()})
        return

    def validate_text(self):
        self.write({'state': 'pass', 'date': fields.datetime.now().date()})
        return

    quantite_piece = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ],
                                      string="Quantité des pièces", )

    integrite_piece = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ],
                                       string="Intégrité des Pièces", )

    point_qualite = fields.Selection([('Après toutes les phases', 'Après toutes les phases'),
                                      ('Contrôle épaisseur', 'Contrôle épaisseur'),
                                      ('Création des mélanges de peinture', 'Création des mélanges de peinture'),
                                      ('Association des mélanges peintures', 'Association des mélanges peintures'),
                                      ],
                                     string="Point Qualité", )

    controle_epaisseur_ts_min = fields.Float("Contrôle épaisseur Min")
    controle_epaisseur_ts_max = fields.Float("Contrôle épaisseur Max")
    controle_epaisseur_ts_moyen = fields.Float("Contrôle épaisseur Moyen")

    adherence_ts = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ], string="Adhérence", )

    controle_epaisseur_peinture_min = fields.Float("Contrôle épaisseur Min")
    controle_epaisseur_peinture_max = fields.Float("Contrôle épaisseur Max")
    controle_epaisseur_peinture_moyen = fields.Float("Contrôle épaisseur Moyen")

    adherence_peinture = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ], string="Adhérence", )

    controle_polymerisation = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ],
                                               string="Contrôle de la polymérisation ", )
    continuite_couche = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ],
                                         string="Continuité de couche", )
    test_colmatage = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ],
                                      string="Test de colmatage", )
    continuite_electrique = fields.Selection([('Conforme', 'Conforme'), ('Non conforme', 'Non conforme'), ],
                                             string="Continuité électrique", )

    controle_epaisseur_cf_min = fields.Float("Contrôle épaisseur Min")
    controle_epaisseur_cf_max = fields.Float("Contrôle épaisseur Max")
    controle_epaisseur_cf_moyen = fields.Float("Contrôle épaisseur Moyen")

    type_peinture = fields.Char("Type peinture")
    lot_base = fields.Char("Lot Base")
    lot_durcisseur = fields.Char("Lot Durcisseur")
    lot_diluant = fields.Char("Lot Diluant")
    temperature = fields.Char("Température")
    hygrometrie = fields.Char("Hygrométrie")
    viscosite = fields.Char("Viscosité")
    date_fabrication = fields.Date("Date de fabrication")

    name = fields.Char(string="Reference", required=True, copy=False, default='/')

    @api.model
    def create(self, vals):
        # Si 'name' n'est pas spécifié, on génère une séquence
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.checks') or '/'
        return super(Quality_check, self).create(vals)

    def validate_quality_check(self):
        """
        Valide le contrôle qualité en comparant les valeurs saisies dans quality.checks avec celles de quality.point.
        """
        for check in self:

            # Vérification des conditions bloquantes
            if check.echantillon == 'non' and check.quantite_controle != check.quantite_fabrique:
                raise UserError(
                    _("La validation est bloquée : la quantité contrôlée doit être égale à la quantité fabriquée lorsque l'échantillon est 'Non'."))
            else:
                # Exemple de conditions pour valider la qualité
                if (check.controle_epaisseur_ts_min == check.quality_point_id.controle_epaisseur_ts_min and
                    check.controle_epaisseur_ts_max == check.quality_point_id.controle_epaisseur_ts_max and
                    check.controle_epaisseur_ts_moyen == check.quality_point_id.controle_epaisseur_ts_moyen and
                    check.adherence_ts == 'Oui'
                ):
                    check.state = 'pass'
                else:
                    check.state = 'fail'




class Quality_alert(models.Model):
    _inherit = 'quality.alert'

    mrp_id = fields.Many2one('mrp.production', string="Production Name")

    @api.model
    def default_get(self, default_fields):
        res = super(Quality_alert, self).default_get(default_fields)
        if self._context.get('mrp_res'):
            mrp_res = self.env['mrp.production'].browse(int(self._context.get('mrp_res')))
            res['product_id'] = mrp_res.product_id.id
            res['product_temp_id'] = mrp_res.bom_id.product_tmpl_id.id
            res['date_assigned'] = fields.datetime.now()
        res = self._convert_to_write(res)
        return res

    @api.model
    def create(self, vals):

        seq = self.env['ir.sequence'].next_by_code('quality.alert') or '/'
        vals['name'] = seq
        if self._context.get('mrp_res'):
            vals['mrp_id'] = int(self._context.get('mrp_res'))

            # mrp_res = self.env['mrp.production'].browse(int(self._context.get('mrp_res')))

        return super(Quality_alert, self).create(vals)

    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True, )
    operation = fields.Many2one('mrp.routing.workcenter', string="Opération")
    type_operation = fields.Selection(related="operation.type_operation")





