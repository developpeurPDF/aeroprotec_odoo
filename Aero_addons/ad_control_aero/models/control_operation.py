# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError, ValidationError



class OperationQualityControl(models.Model):
    _name = 'operation.quality.control'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char("Libellé", required=True) #, copy=False, readonly=True, default='Nouveau'

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', 'Nouveau') == 'Nouveau':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('operation.quality.control') or 'Nouveau'
    #     return super(OperationQualityControl, self).create(vals)


    production_id = fields.Many2one('mrp.production',string="Ordre de fabrication")
    workorder_id = fields.Many2one('mrp.workorder', string="Ordre de travail", domain="[('production_id', '=', production_id)]")
    description = fields.Html("Description")
    type_valeur = fields.Selection([
        ('numerique_surveillance', 'Numérique avec surveillance'),], string="Type de la valeur", ) #, groups="hr.group_hr_user"
    type_outil = fields.Selection([
        ('1', '1'),],string="Type d'outil de mesure",  )


    niveau_criticite = fields.Selection([('defaut', 'Niveau par défaut'),], string="Niveau de criticité", )

    declenche_non_conformite = fields.Selection([('Oui', 'Oui'),('Non', 'Non'), ],
                                                string="Déclenche une fiche de non conformité en cas de mesures non conformités",  )

    affiche_cible = fields.Selection([('Oui', 'Oui'), ('Non', 'Non'), ],
                                                string="Afficher la cible",
                                                 )
    taille_echant = fields.Selection([('1', '1'), ('2', '2'), ],
                                     string="Taille échant",
                                      )

    uom_id = fields.Many2one(
        'uom.uom',  # product.uom
        string='Unité',
        required=True,
    )
    # Cible
    critere_cible = fields.Selection([('fixe', 'Valeur fixe'), ],
                                                string="Critère",
                                                 )

    valeur_cible = fields.Float("Valeurs")

    # Limite de surveillance inférieure

    attribut_surveillance_inferieure = fields.Selection([('Relatif', 'Relatif'), ],
                                     string="Attribut",
                                      )

    critere_surveillance_inferieure = fields.Selection([('fixe', 'Valeur fixe'), ],
                                     string="Critère",
                                      )

    valeur_surveillance_inferieure = fields.Float("Valeurs")

    # Limite de surveillance supérieure

    attribut_surveillance_superieure = fields.Selection([('Relatif', 'Relatif'), ],
                                                        string="Attribut",
                                                         )

    critere_surveillance_superieure = fields.Selection([('fixe', 'Valeur fixe'), ],
                                                       string="Critère",
                                                        )

    valeur_surveillance_superieure = fields.Float("Valeurs")

    # Limite de controle inférieure

    attribut_controle_inferieure = fields.Selection([('Relatif', 'Relatif'), ],
                                                        string="Attribut",)

    critere_controle_inferieure = fields.Selection([('fixe', 'Valeur fixe'), ],
                                                       string="Critère",)

    valeur_controle_inferieure = fields.Float("Valeurs")


    # Limite de controle supérieure

    attribut_controle_superieure = fields.Selection([('Relatif', 'Relatif'), ],
                                                       string="Attribut",
                                                        )

    critere_controle_superieure = fields.Selection([('fixe', 'Valeur fixe'), ],
                                                       string="Critère",
                                                        )

    valeur_controle_superieure = fields.Float("Valeurs")

    # Conditions d'exécution
    conditions_execution = fields.Many2many(
        'operation.quality.control.condition.execution',
        string="Conditions d'exécution",
        relation='quality_control_condition_execution_rel'  # Nom explicite de la table de relation
    )    # Documentation
    worksheet_ids = fields.Many2many('mrp.routing.worksheets', string="Documenatation")



class OperationQualityControlConditionExecution(models.Model):
    _name = 'operation.quality.control.condition.execution'

    critere = fields.Selection([('OF', 'OF'), ],
                                     string="Critère",
                                      )

    information = fields.Selection([('OF_TYPE_TRAITEMENT', 'OF_TYPE_TRAITEMENT'),
                                    ('OF_NUM_LIGNE', 'OF_NUM_LIGNE'),
                                    ('OF_ORDRE_OPERATION', 'OF_ORDRE_OPERATION'),
                                    ('OF_CODE_OPERATION', 'OF_CODE_OPERATION'),
                                    ('OF_DATE_PREVISIONNELLE_DE_PASSAGE', 'OF_DATE_PREVISIONNELLE_DE_PASSAGE'),
                                    ('OF_TYPE_CND', 'OF_TYPE_CND'),
                                    ('OF_NIV_CND', 'OF_NIV_CND'),
                                    ('OF_BRINNEL', 'OF_BRINNEL'),
                                    ('OF_VICKERS', 'OF_VICKERS'),
                                    ('OF_CODE_ACCREDITATION', 'OF_CODE_ACCREDITATION'),
                                    ('OF_NIV_ACCREDITATION', 'OF_NIV_ACCREDITATION'),
                                    ('OF_CONTROLE_VISUEL', 'OF_CONTROLE_VISUEL'),
                                    ('OF_OPERATION_CC', 'OF_OPERATION_CC'),
                                    ('OF_REGLE_PRELEVEMENT', 'OF_REGLE_PRELEVEMENT'),
                                    ('OF_IMPRESSION_CC', 'OF_IMPRESSION_CC'),
                                    ('OF_ILOT', 'OF_ILOT'),
                                    ('OF_GROUP_EP', 'OF_REGLE_PRELEVEMENT'),
                                    ],
                                     string="Critère",
                                      )
    operateur = fields.Selection([('Contient', 'Contient'),('Existe', 'Existe'), ],
                                                       string="Opérateur",)
    valeur = fields.Float("Valeurs")

# class MrpWorkorder(models.Model):
#     _inherit = 'mrp.workorder'
#
#     quality_control_id = fields.Many2one(
#         'operation.quality.control', string="Contrôle Qualité", readonly=True,
#         help="Lien vers le contrôle qualité lié à cet ordre de travail"
#     )
#
#     def action_create_quality_control(self):
#         """Créer un contrôle opération lié à cet ordre de travail"""
#         self.ensure_one()  # Assurez-vous qu'une seule ligne est sélectionnée
#
#         if self.quality_control_id:
#             raise UserError(_("Un contrôle qualité existe déjà pour cet ordre de travail."))
#         quality_control = self.env['operation.quality.control'].create({
#             'description': f"Contrôle {self.name}",
#             'uom_id': self.production_id.product_uom_id.id,
#             'workorder_id': self.id,
#             'production_id': self.production_id.id,
#         })
#
#         self.quality_control_id = quality_control
#         # Rediriger vers la vue form du contrôle créé
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Contrôle Opération',
#             'res_model': 'operation.quality.control',
#             'view_mode': 'form',
#             'res_id': quality_control.id,
#             'target': 'current',
#         }
