from odoo import api, fields, models, _
from math import pi

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string="Nomenclature")
    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre")
    nom_donneur_order = fields.Char(string="Nom du Donneur d'ordre", related='donneur_order.name.name', readonly=True)
    codes = fields.Many2one('donneur.ordre.code', string="Code traitement" , domain="[('name_donneur_order', '=', nom_donneur_order)]" )
    nb_traitement_surface = fields.Integer(string="Nombre de traitement de surface")
    state = fields.Selection(
        selection=[
            ('brouillon', 'Brouillon'),
            ('redige', 'Rédigé'),
            ('verifie', 'Vérifié'),
            ('approve', 'Approuvé'),
        ],
        string='Status',
        copy=False,
        tracking=True,
        default='brouillon',
    )


    redacteur = fields.Many2one('res.partner', string="Rédacteur")
    date_redaction = fields.Datetime( string="Date de rédaction")
    verificateur = fields.Many2one('res.partner', string="Vérificateur")
    date_verification = fields.Datetime(string="Date de vérification")
    approbateur = fields.Many2one('res.partner', string="Approbateur ")
    date_approbation = fields.Datetime(string="Date de approbation")

    def reset_draft(self):
        self.write({'state': 'brouillon'})

    def action_redige(self):
        self.write({'state': 'redige'})

    def action_verifie(self):
        self.write({'state': 'verifie'})

    def action_approve(self):
        self.write({'state': 'approve'})


