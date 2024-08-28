from odoo import models, fields, api, _

class PoidsCarbone(models.Model):
    _name = "poids.carbone"

    name = fields.Char("Nom")
    poids_carbone = fields.Float("Poids Carbone")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)


class ResCompany(models.Model):
    _inherit = 'res.company'

    poids_carbone = fields.Many2one("poids.carbone", string="Poids Carbone")
    afaq = fields.Image("Logo AFAQ")
    utiliser_afaq = fields.Boolean("Utilisé Logo AFAQ")
    nadscap = fields.Image("Logo NADSCAP ")
    utiliser_nadscap = fields.Boolean("Utilisé Logo NADSCAP ")
    n_quality = fields.Char("Qualité")

