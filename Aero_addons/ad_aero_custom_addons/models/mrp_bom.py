from odoo import api, fields, models, _
from math import pi
from collections import defaultdict

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string="Libellé de la gamme", tracking=True)
    # code = fields.Char('Reference',compute='_compute_code' )
    modele = fields.Char(string="Modèle de la gamme", tracking=True)
    donneur_order = fields.Many2one('donneur.order',related="product_tmpl_id.donneur_order", string="Donneur d'ordre", tracking=True)
    indice = fields.Char(string="Indice", related="product_tmpl_id.indice", tracking=True)
    norme = fields.Many2one('norme',string="Norme", related="product_tmpl_id.norme", tracking=True)
    nom_donneur_order = fields.Char(string="Nom du Donneur d'ordre", related='donneur_order.name.name', readonly=True)
    codes = fields.Many2one('donneur.ordre.code', string="Code traitement" , domain= "[('name_donneur_order', '=', nom_donneur_order)]", tracking=True )
    nb_traitement_surface = fields.Integer(string="Nombre de traitement de surface")
    state = fields.Selection(
        selection=[
            ('brouillon', 'Brouillon'),
            ('redige', 'Rédigé'),
            ('verifie', 'Vérifié'),
            ('approve', 'Approuvé'),
            ('active', 'Active'),
        ],
        string='Status',
        copy=False,
        tracking=True,
        default='brouillon',
    )

    def _default_employee(self):
        return self.env.user.employee_id

    redacteur = fields.Many2one('res.partner', string="Rédacteur", default=_default_employee, tracking=True)
    date_redaction = fields.Datetime( string="Date de rédaction", tracking=True)
    verificateur = fields.Many2one('res.partner', string="Vérificateur", default=_default_employee, tracking=True)
    date_verification = fields.Datetime(string="Date de vérification")
    approbateur = fields.Many2one('res.partner', string="Approbateur ", default=_default_employee, tracking=True)
    date_approbation = fields.Datetime(string="Date d'approbation", tracking=True)
    is_locked = fields.Boolean(string="Locked", help="Check this box to lock product modifications.")

    def reset_draft(self):
        self.write({'state': 'brouillon'})

    def action_redige(self):
        self.write({'state': 'redige'})

    def action_verifie(self):
        self.write({'state': 'verifie'})

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_active(self):
        self.write({'state': 'active'})
        self.ensure_one()
        self.is_locked = not self.is_locked
        return True

    # @api.model
    # def _compute_code(self):
    #     for rec in self:
    #         # Génération de la référence en utilisant le code de produit, le code de norme et le code de traitement
    #         product_code = rec.product_tmpl_id.indice
    #         standard_code = rec.codes.name
    #         treatment_code = rec.norme.indice
    #         print('product_code', product_code)
    #         print('standard_code', standard_code)
    #         print('treatment_code', treatment_code)
    #
    #         reference = f"{product_code}-{standard_code}-{treatment_code}"
    #
    #         # Ajout de la référence aux valeurs avant de créer la nomenclature
    #         rec.code = reference

            # Appel de la méthode create du modèle parent avec les valeurs modifiées
            # return super(MrpBom, self).create(rec.code)


    evolution = fields.Boolean(string="Evolution Effectué", default=False, readonly=True)
    reference_premier_document = fields.Many2one('mrp.bom', string="Référence du premier document", copy=False,
                                                 readonly=True)
    date_derniere_duplication = fields.Datetime(string="Date de dernière duplication", copy=False, readonly=True)

    @api.model
    def duplicate_bom(self, bom_id):

        bom_original = self.browse(bom_id)
        num_duplications = self.search_count([('reference_document_duplicated', '=', bom_original.id)])

        bom_copy_data = {
            'name': f"{bom_original.name} V {num_duplications + 1}",
            'modele': bom_original.modele,
            'donneur_order': bom_original.donneur_order.id,
            'indice': bom_original.indice,
            'norme': bom_original.norme.id,
            'product_tmpl_id': bom_original.product_tmpl_id.id,

            'state': 'brouillon',  # Vous pouvez définir l'état initial ici
            'date_redaction': False,  # Réinitialiser la date de rédaction
            'date_verification': False,  # Réinitialiser la date de vérification
            'date_approbation': False,  # Réinitialiser la date d'approbation
            'is_locked': False,  # Réinitialiser l'état de verrouillage
            'reference_premier_document': bom_original.id,  # Réinitialiser la référence du premier document
            'date_derniere_duplication': fields.Datetime.now(),
            'evolution': False,
        }

        # Créer la copie
        new_bom = self.create(bom_copy_data)
        for bom_line in bom_original.bom_line_ids:
            bom_line_copy_data = {
                'bom_id': new_bom.id,
                'product_id': bom_line.product_id.id,
                'product_qty': bom_line.product_qty,
                'product_uom_id': bom_line.product_uom_id.id,
                'operation_id': bom_line.operation_id.id if bom_line.operation_id else False,
            }
            self.env['mrp.bom.line'].create(bom_line_copy_data)

        for operation in bom_original.operation_ids:
            operation_copy_data = {
                'bom_id': new_bom.id,
                'name': operation.name,
                'workcenter_id': operation.workcenter_id.id,
                'time_cycle': operation.time_cycle,
                'sequence': operation.sequence,
            }
            self.env['mrp.routing.workcenter'].create(operation_copy_data)


        bom_original.write({'evolution': True})

        return {
            'name': _('Duplicate BoM'),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'mrp.bom',
            'res_id': new_bom.id,
            'type': 'ir.actions.act_window',
        }
