from collections import defaultdict
from odoo import api, fields, models, _

class Quality_check(models.Model):
    _name = 'quality.checks.line'


    point_qualite = fields.Selection([('Après toutes les phases', 'Après toutes les phases'),
                                      ('Opérations de TS', 'Opérations de TS'),
                                      ('Opérations de Peinture', 'Opérations de Peinture'),
                                      ('Contrôle des délais interopération', 'Contrôle des délais interopération'),
                                      ('Contrôle final', 'Contrôle final'),
                                      ('Création des mélanges de peinture', 'Création des mélanges de peinture'),
                                      ('Association des mélanges peintures', 'Association des mélanges peintures'),
                                      ],
                                     string="Point Qualité", related="quality_checks_ids.point_qualite")

    quality_checks_ids = fields.Many2one(
        comodel_name='quality.checks',
        string="Contrôle",
        required=True, ondelete='cascade', index=True, copy=False)





    quntite_controle = fields.Integer("Quantité contrôlée")

    quantite_piece = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ],
                                      string="Quantité des pièces", )

    integrite_piece = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ],
                                       string="Intégrité des Pièces", )

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
    lot_base = fields.Char("Base du lot")
    lot_durcisseur = fields.Char("Lot Durcisseur")
    lot_diluant = fields.Char("Lot Diluant")
    temperature = fields.Char("Température")
    hygrometrie = fields.Char("Hygrométrie")
    viscosite = fields.Char("Viscosité")
    date_fabrication = fields.Date("Date de fabrication")