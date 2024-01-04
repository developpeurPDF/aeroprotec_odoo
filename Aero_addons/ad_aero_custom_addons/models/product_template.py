# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
    famille_matiere = fields.Many2one('matiere.parameter', string="Famille matière")
    # matiere = fields.Many2one('matiere.parameter', string="Famille matière")
    famille_matiere_name = fields.Char("Nom famille matière", related="famille_matiere.name", readonly=True, store=True)
    matiere = fields.Many2one('matiere.parameter.value', string="Matière",
                           domain="[('parameter_name','=', famille_matiere_name)]")
    matiere_name = fields.Char(string="Nom matière", related="matiere.name", readonly=True, store=True)
    ref_matiere = fields.Many2one('matiere.parameter.ref', string="Réf matière",
                           domain="[('parameter_name','=', matiere_name)]")
    ref_matiere_name = fields.Char(string="Nom matière", related="ref_matiere.name", readonly=True, store=True)
    coeff_avion = fields.Integer(string="Coeff avion")
    masque_impression = fields.Char(string="Masque Impression")



    resistance_matiere = fields.Many2one('matiere.parameter.resistance', string="Résistance matière",
                                         domain="[('parameter_name','=', ref_matiere_name)]")

    activite = fields.Many2one('activite', string="Activité",)
    motif_blocage_lancement = fields.Many2one('motif.blocage.lancement', string="Motif de blocage de lancement",)
    classe_fonctionnelle = fields.Many2one('classe.fonctionnelle', string="Classe fonctionnelle",)
    programme_aeonautique = fields.Many2one('programme.aeonautique', string="Programme aéronautique",)
    test = fields.Char(string="test")
    test2 = fields.Char(string="test 2")
    test3 = fields.Char(string="test 3")
    test4 = fields.Char(string="test 4")
    test5 = fields.Char(string="test 5")

    def _compute_air(self):
        for rec in self:
            if rec.forme == "cube":
                rec.surface = (((rec.hauteur * rec.diametre * pi) +(2 * pi * (rec.diametre/2)) * (rec.diametre /2)))/10000
            elif rec.forme == "cylindre":
                rec.surface = (((rec.longueur * rec.largeur) + (rec.longueur * rec.hauteur) + (rec.largeur * rec.hauteur)) * 2)/10000
            else:
                rec.surface = 0





