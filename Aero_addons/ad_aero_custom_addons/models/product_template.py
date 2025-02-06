# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_locked = fields.Boolean(string="Locked", help="Check this box to lock product modifications.")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    allow_multiple_boms = fields.Boolean(string='Autoriser plusieurs nomenclatures', default=False)

    def toggle_lock(self):
        self.ensure_one()
        self.is_locked = not self.is_locked
        return True

    code = fields.Integer("Code", tracking=True)
    plan_reference = fields.Char("Référence plan", tracking=True)

    forme = fields.Selection(selection=[
            ('cube','Cube'),
            ('cylindre','Cylindre')],
        string='Forme', help="Permet de déterminer l’encombrement et la surface à traiter", tracking=True)
    hauteur = fields.Float("Hauteur", tracking=True)
    largeur = fields.Float("Largeur", tracking=True)
    longueur = fields.Float("Longueur", tracking=True)

    @api.depends('longueur')
    def _compute_cost(self):
        for template in self:
            original_cost = template.standard_price
            # Double the cost if length exceeds 600 mm
            if template.longueur > 600:
                template.standard_price = original_cost * 2
            else:
                template.standard_price = original_cost

    def action_bom_cost(self):
        # Your existing logic
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        if templates:
            templates.mapped('product_variant_id').action_bom_cost()

        # Ensure cost adjustment based on length is applied
        self._compute_cost()

    def button_bom_cost(self):
        # Your existing logic
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        if templates:
            templates.mapped('product_variant_id').button_bom_cost()

        # Ensure cost adjustment based on length is applied
        self._compute_cost()
    
    
    
    diametre = fields.Float("Diamètre", tracking=True)
    surface = fields.Float("Surface", compute='_compute_air')
    surface_traiter = fields.Char("Surface à traiter", tracking=True)

    type_article = fields.Selection(selection=[
            ('Production','Production'),
            ('Eprouvette','Eprouvette'),
            ('Composant','Composant'),
            ('Outillage','Outillage'),
    ],
        string="Type d'article", tracking=True)
    famille_matiere = fields.Many2one('matiere.parameter', string="Famille matière", tracking=True,  domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    # matiere = fields.Many2one('matiere.parameter', string="Famille matière")
    famille_matiere_name = fields.Char("Nom famille matière", related="famille_matiere.name", readonly=True, store=True)
    matiere = fields.Many2one('matiere.parameter.value', string="Matière",
                           domain="[('parameter_name','=', famille_matiere_name)]", tracking=True)
    matiere_abreviation = fields.Char(string="Abréviation matière", related="matiere.name_abreviation", readonly=True, store=True)
    matiere_name = fields.Char(string="Nom matière", related="matiere.name", readonly=True, store=True)
    ref_matiere = fields.Many2one('matiere.parameter.ref', string="Nature matière",
                           domain="[('parameter_name','=', matiere_name)]", tracking=True)
    ref_matiere_name = fields.Char(string="Nom matière", related="ref_matiere.name", readonly=True, store=True)
    resistance_matiere = fields.Char(string="Résistance matière", related="ref_matiere.name_resistance", tracking=True)

    coeff_avion = fields.Integer(string="Coeff avion", tracking=True)
    masque_impression = fields.Char(string="Masque impression marqueuse", tracking=True)
    info_marquer = fields.Char(string="Information à marquer", tracking=True)
    n_ft = fields.Char(string="N° FT", tracking=True)
    piece_jointe_ft = fields.Binary(string="Pièce jointe FT", tracking=True)
    norme_douaniere = fields.Char(string="Norme douanière", tracking=True)

    indice = fields.Char(string="Indice", tracking=True)

    type_indice = fields.Selection(selection=[
        ('piece', 'Indice pièce'),
        ('plan', 'Indice plan'),
        ('nomenclature', 'Indice nomenclature'),
        ('planfi', 'Indice FI'),
    ],
        string='Type d’indice', tracking=True)
    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True)
    client = fields.Many2one('res.partner', string="Client", tracking=True)
    memo = fields.Text(string="Mémo")


    activite = fields.Many2one('activite', string="Activité", tracking=True)
    motif_blocage_lancement = fields.Many2one('motif.blocage.lancement', string="Motif de blocage de lancement", tracking=True,)
    classe_fonctionnelle = fields.Many2one('classe.fonctionnelle', string="Classe fonctionnelle", tracking=True,)
    programme_aeonautique = fields.Many2one('programme.aeonautique', string="Programme aéronautique", tracking=True,)
    # norme = fields.Many2one('norme', string="Norme", tracking=True,)

    gerer_stock = fields.Selection(string="Géré en stock", selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ], compute='_compute_gerer_stock')

    gestion_lots = fields.Selection(string="Gestion de lots", selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ], tracking=True)
    gestion_sortie_auto = fields.Selection(string="Gestion des sorties de stock auto", selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ], tracking=True)

    @api.onchange('custom_bom_id')
    def _onchange_custom_bom_id(self):
        if self.custom_bom_id:
            self.produce_delay = self.custom_bom_id.produce_delay
        else:
            self.produce_delay = 0.0


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



    # frais = fields.Many2many('frais',
    #                          string="Frais", readonly=False)
