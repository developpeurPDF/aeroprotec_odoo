from odoo import api, fields, models, _
from datetime import datetime, date
from math import pi

class Norme(models.Model):
    _name = 'norme'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    indice = fields.Char(string="Indice", tracking=True, required=True,)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    name = fields.Char(string="Libellé",required=True, tracking=True,)
    type_norme = fields.Selection([
            ('interne', 'Norme Interne'),
            ('externe', 'Norme Externe')],
        string="Type de la norme", store=True, tracking=True, required=True,)
    user_id = fields.Many2one('res.users', string="Valideur interne", tracking=True,)
    employee_id = fields.Many2one('hr.employee', string="Validateur", tracking=True, readonly=True)
    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True,)
    designation = fields.Char(string="Designation", tracking=True,required=True,)
    docs = fields.Binary(string="Docs", tracking=True,)
    # date = fields.Date(string="Date de qualification")
    observation = fields.Char(string="Observation", tracking=True,)
    qualifie = fields.Selection([
        ('Oui', 'Oui'),
        ('Non', 'Non')],
        string="Qualifié", store=True, tracking=True,)

    state = fields.Selection(
        selection=[
            ('en_projet', 'En projet'),
            ('conforme', 'Qualifiée'),
            ('derogation', 'Dérogation'),
            ('non_conforme', 'Non applicable'),
            ('archived', 'Archivée'),
        ],
        string='Status',
        copy=False,
        tracking=True,
        default='en_projet',
    )

    # def _default_employee(self):
    #     return self.env.user.employee_id
    # valider_par = fields.Many2one('res.users', string="Valider par", default=_default_employee)
    date_validation = fields.Datetime(string="Date de qualification")
    date_archived = fields.Datetime(string="Date d'archivage")

    def reset_draft(self):
        self.write({'state': 'en_projet'})

    def action_non_conforme(self):
        self.write({'state': 'non_conforme'})
        self.qualifie = "Non"

    def action_derogation(self):
        self.write({'state': 'derogation'})

    def action_archived(self):
        self.write({'state': 'archived'})
        self.date_archived = datetime.now()
        self.ensure_one()
        self.is_locked = True
        return True

    def action_active(self):
        self.write({'state': 'conforme'})
        # self.ensure_one()
        # self.is_locked = not self.is_locked

        # Ajout automatique de la date de validation
        # self.employee_id = self.env.user  # Utilisateur actuel
        self.date_validation = datetime.now()
        self.qualifie = "Oui"
        self.ensure_one()
        self.is_locked = not self.is_locked
        self.employee_id = self.env.user.employee_id.id

        return True

    num_rapport_qualification = fields.Char(string="N° de rapport de qualification", tracking=True)
    date_premiere_qualification = fields.Datetime(string="Date de première qualification", tracking=True)
    date_fin_validite = fields.Datetime(string="Date de fin de validité", tracking=True)
    date_fin_derogation = fields.Datetime(string="Date de fin de dérogation", tracking=True)
    note_en_projet = fields.Html(string="Note")
    note_qualifie = fields.Html(string="Note")
    note_derogation = fields.Html(string="Note")

    is_locked = fields.Boolean(string="Locked", help="Check this box to lock product modifications.")


    # Fonction dipliquée

    reference_premier_document = fields.Many2one('norme',string="Référence du premier document", copy=False, readonly=True)
    date_derniere_duplication = fields.Datetime(string="Date de dernière duplication", copy=False, readonly=True)
    evolution = fields.Boolean(string="Evolution Effectué", default=False, readonly=True, tracking=True)

    @api.model
    def duplicate_norme(self, norme_id):
        # Récupérer l'enregistrement d'origine
        norme_original = self.browse(norme_id)

        # Incrémenter l'indice en fonction de sa valeur actuelle
        indice = norme_original.indice
        new_indice = ''
        numeric_part = ''
        alpha_part = ''
        for char in indice:
            if char.isdigit():
                numeric_part += char
            else:
                alpha_part += char

        if numeric_part.isdigit():
            numeric_part = str(int(numeric_part) + 1)
        # elif alpha_part.isdigit():

        else:
            numeric_part = str(int(''.join(filter(str.isdigit, numeric_part))) + 1) if numeric_part else ''
        if not any(
                char.isdigit() for char in numeric_part):  # Vérifier si la partie alphabétique ne contient aucun chiffre
            if alpha_part:
                alpha_part = chr(ord(alpha_part) + 1)

        new_indice = alpha_part + numeric_part


        # Créer une copie avec un indice incrémenté de 1
        norme_copy_data = {
            'name': str(norme_original.name) +" V2 ",
            'type_norme': norme_original.type_norme,
            'user_id': norme_original.user_id.id,
            'employee_id': norme_original.employee_id.id,
            'donneur_order': norme_original.donneur_order.id,
            'designation': norme_original.designation,
            'docs': norme_original.docs,
            'observation': norme_original.observation,
            'qualifie': False,
            'state': 'en_projet',  # Vous pouvez définir l'état initial ici
            'date_validation': False,  # Réinitialiser la date de validation
            'num_rapport_qualification': False,  # Réinitialiser le numéro de rapport
            'date_premiere_qualification': False,  # Réinitialiser la date de première qualification
            'date_fin_validite': False,  # Réinitialiser la date de fin de validité
            'date_fin_derogation': False,  # Réinitialiser la date de fin de dérogation
            'note_en_projet': False,  # Réinitialiser la note en projet
            'note_qualifie': False,  # Réinitialiser la note qualifié
            'note_derogation': False,  # Réinitialiser la note de dérogation
            'reference_premier_document': norme_original.id,  # Réinitialiser la référence du premier document
            'date_derniere_duplication': fields.Datetime.now(),  # Mettre à jour la date de dernière duplication
            'indice': new_indice,  # Mettre à jour l'indice
            'evolution': False,
        }

        # Créer la copie
        new_norme = self.create(norme_copy_data)
        # Mettre à jour l'indice
        # new_norme.write({'indice': str(int(norme_original.indice) + 1)})
        norme_original.write({'evolution': True})

        return {
            'name': _('Duplicate Norme'),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'norme',
            'res_id': new_norme.id,
            'type': 'ir.actions.act_window',
        }
    operation_ni = fields.One2many('mrp.routing.workcenter','norme_interne',string="Opération NI")
    operation_ne = fields.One2many('mrp.routing.workcenter','norme_externe',string="Opération NE")
