from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    return_cont_env = fields.Boolean(string="Contribution énergétique et Contribution environnementale", default=False)

    # ad_montant_rg = fields.Float("Montant du taux contribution énergétique", related='company_id.ad_montant_rg')

    # ad_montant_cee = fields.Float("Montant du taux contribution environnementale", related='company_id.ad_montant_cee')
    contribution_enrg = fields.Boolean(string="Contribution énergétique", default=True)
    contribution_env = fields.Boolean(string="Contribution environnementale", default=True)
