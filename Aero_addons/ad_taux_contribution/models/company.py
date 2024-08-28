# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    ad_cee_account_id = fields.Many2one("account.account", "Compte comptable de contribution environnementale")
    ad_montant_cee = fields.Float("Taux contribution environnementale")
    ad_tva_cee_account_id = fields.Many2one("account.account", "Compte comptable de TVA de contribution environnementale")
    ad_tva_cee = fields.Float("TVA appliqué sur le Taux contribution environnementale")

    ad_rg_account_id = fields.Many2one("account.account", "Compte comptable de contribution énergétique")
    ad_montant_rg = fields.Float("Taux contribution énergétique")
    ad_tva_rg_account_id = fields.Many2one("account.account", "Compte comptable de TVA de contribution énergétique")
    ad_tva_rg = fields.Float("TVA appliqué sur le Taux contribution énergétique")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
