# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_locked = fields.Boolean(string="Locked", help="Check this box to lock product modifications.")


    def toggle_lock(self):
        self.ensure_one()
        self.is_locked = not self.is_locked
        return True

    code = fields.Integer("Code")
    plan_reference = fields.Char("Référence plan")

    forme = fields.Selection(selection=[
            ('cube','Cube'),
            ('cylindre','Cylindre')],
        string='Forme', help="Permet de déterminer l’encombrement et la surface à traiter")
    hauteur = fields.Float("Hauteur")
    largeur = fields.Float("Largeur")
    longueur = fields.Float("Longueur")
    diametre = fields.Float("Diamètre")
    surface = fields.Float("Surface", compute='_compute_air')
    surface_traiter = fields.Char("Surface à traiter")
    type_montage = fields.Selection(selection=[
            ('CADRE_SIMPLE','CADRE SIMPLE'),
            ('CADRE_DOUBLE','CADRE DOUBLE'),
            ('MONTAGE_TOURNANT','MONTAGE TOURNANT'),
    ],
        string='Type de montage')
    type_article = fields.Selection(selection=[
            ('Production','Production'),
            ('Eprouvette','Eprouvette'),
            ('Composant','Composant'),
            ('Outillage','Outillage'),
    ],
        string="Type d'article")
    famille_matiere = fields.Many2one('matiere.parameter', string="Famille matière")
    # matiere = fields.Many2one('matiere.parameter', string="Famille matière")
    famille_matiere_name = fields.Char("Nom famille matière", related="famille_matiere.name", readonly=True, store=True)
    matiere = fields.Many2one('matiere.parameter.value', string="Matière",
                           domain="[('parameter_name','=', famille_matiere_name)]")
    matiere_abreviation = fields.Char(string="Abréviation matière", related="matiere.name_abreviation", readonly=True, store=True)
    matiere_name = fields.Char(string="Nom matière", related="matiere.name", readonly=True, store=True)
    ref_matiere = fields.Many2one('matiere.parameter.ref', string="Nature matière",
                           domain="[('parameter_name','=', matiere_name)]")
    ref_matiere_name = fields.Char(string="Nom matière", related="ref_matiere.name", readonly=True, store=True)
    resistance_matiere = fields.Char(string="Résistance matière", related="ref_matiere.name_resistance")

    coeff_avion = fields.Integer(string="Coeff avion")
    masque_impression = fields.Char(string="Masque impression marqueuse")
    info_marquer = fields.Char(string="Information à marquer")
    n_ft = fields.Char(string="N° FT")
    piece_jointe_ft = fields.Binary(string="Pièce jointe FT")
    norme_douaniere = fields.Char(string="Norme douanière")

    indice = fields.Char(string="Indice")
    nb_piece_barre = fields.Integer(string="Nombre de pièces par barre")
    type_indice = fields.Selection(selection=[
        ('piece', 'Indice pièce'),
        ('plan', 'Indice plan'),
        ('nomenclature', 'Indice nomenclature'),
        ('planfi', 'Indice FI'),
    ],
        string='Type d’indice ')
    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre")
    client = fields.Many2one('res.partner', string="Client")
    memo = fields.Text(string="Mémo")


    activite = fields.Many2one('activite', string="Activité",)
    motif_blocage_lancement = fields.Many2one('motif.blocage.lancement', string="Motif de blocage de lancement",)
    classe_fonctionnelle = fields.Many2one('classe.fonctionnelle', string="Classe fonctionnelle",)
    programme_aeonautique = fields.Many2one('programme.aeonautique', string="Programme aéronautique",)

    gerer_stock = fields.Selection(string="Géré en stock", selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ], compute='_compute_gerer_stock')

    gestion_lots = fields.Selection(string="Gestion de lots", selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ])
    gestion_sortie_auto = fields.Selection(string="Gestion des sorties de stock auto", selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ])



    def _compute_gerer_stock(self):
        for rec in self:
            if rec.detailed_type == "product":
                rec.gerer_stock = "Oui"
            else:
                rec.gerer_stock = "Non"


    def _compute_air(self):
        for rec in self:
            if rec.forme == "cylindre":
                rec.surface = (((rec.hauteur * rec.diametre * pi) +(2 * pi * (rec.diametre/2)) * (rec.diametre /2)))/10000
            elif rec.forme == "cube":
                rec.surface = (((rec.longueur * rec.largeur) + (rec.longueur * rec.hauteur) + (rec.largeur * rec.hauteur)) * 2)/10000
            else:
                rec.surface = 0




