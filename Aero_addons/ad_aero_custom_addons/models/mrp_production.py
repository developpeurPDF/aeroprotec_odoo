from odoo import api, fields, models, _
from math import pi

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre")
    nom_donneur_order = fields.Char(string="Nom du Donneur d'ordre", related='donneur_order.name.name', readonly=True)
    codes = fields.Many2one('donneur.ordre.code', string="Code traitement" , domain="[('name_donneur_order', '=', nom_donneur_order)]" )
    # code_traitement = fields.Char(string="Code traitement", related="donneur_order.codes")
