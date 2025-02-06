
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Quality_check(models.Model):
    _inherit = 'quality.checks'

    non_conformite_id = fields.Many2one("non.conformite", string="Non Conformité",)
    moyen_controle = fields.Char(string="Moyen de contrôle")
    qte_concernee = fields.Float(string="Qté Concernée (%)", compute="_compute_qte_concernee")

    @api.depends('quantite_controle', 'quantite_fabrique')
    def _compute_qte_concernee(self):
        for record in self:
            if record.quantite_fabrique: 
                record.qte_concernee = (record.quantite_controle / record.quantite_fabrique) * 100
            else:
                record.qte_concernee = 0.0

    def action_create_non_conformite(self):
        """Crée une fiche de non-conformité liée à ce contrôle qualité."""
        for check in self:
            if not check.non_conformite_id:  # Vérifie qu'une NC n'existe pas déjà
                non_conformite_vals = {
                    # 'name': 'Nouveau',
                    'quality_checks_id': check.id,  # Exemple : peut être modifié selon la logique métier
                    #'produit': check.product_id.id,  # Exemple : peut être modifié selon la logique métier
                    'commande_initiale': check.workorder_id.production_id.sale_order_line_id.order_id.id if check.workorder_id else False,
                    'of_initiale': check.workorder_id.production_id.id if check.workorder_id else False,
                    'raison_sociale_client': check.workorder_id.production_id.sale_order_line_id.order_id.partner_id.name if check.workorder_id else '',
                    'reference_article': check.product_id.default_code if check.product_id else '',
                    'designation_article': check.product_id.name if check.product_id else '',
                    'quantite_nc': check.quantite_non_conforme,
                    'ilot_machine_responsable': check.workorder_id.workcenter_id.id if check.workorder_id else False,
                    'utilisateur_creation_nc': self.env.user.id,
                    'ref_commande_client': check.workorder_id.production_id.sale_order_line_id.order_id.client_order_ref if check.workorder_id else False,
                    'of': check.mrp_id.id if check.mrp_id else False,
                    'produit': check.product_id.id,
                }
                # Créer la non-conformité
                non_conformite = self.env['non.conformite'].create(non_conformite_vals)
                # Lier la NC au contrôle qualité
                check.non_conformite_id = non_conformite.id
                if check.workorder_id:
                    check.workorder_id.state = 'nci_waiting'
                    check.workorder_id.button_pending()

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'non.conformite',
                    'view_mode': 'form',
                    'res_id': non_conformite.id,
                    'target': 'current',
                }
            else:
                raise UserError("Une fiche de non-conformité est déjà liée à ce contrôle qualité.")

class Quality_point(models.Model):
    _inherit = 'quality.alert'

    type_defaut = fields.Many2one('type.defaut', string="Type de Défaut", tracking=True)
    causes_non_conformite = fields.Many2one(
        'cause.non.conformite',
        string="Causes de la Non-Conformité", tracking=True
    )

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    nc_ids = fields.One2many('non.conformite', 'of', string="Non conformité")
  