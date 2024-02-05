from odoo import api, fields, models, _
from math import pi

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True)
    nom_donneur_order = fields.Char(string="Nom du Donneur d'ordre", related='donneur_order.name.name', readonly=True)
    codes = fields.Many2one('donneur.ordre.code', string="Code traitement" , domain="[('name_donneur_order', '=', nom_donneur_order)]", tracking=True)
    # code_traitement = fields.Char(string="Code traitement", related="donneur_order.codes")

    @api.depends('product_id')
    def _compute_bom_id(self):
        super(MrpProduction, self)._compute_bom_id()

        # Ajoutez votre logique personnalisée ici pour filtrer les BOM avec le state 'active'
        for production in self:
            if production.bom_id and production.bom_id.state != 'active':
                production.bom_id = False