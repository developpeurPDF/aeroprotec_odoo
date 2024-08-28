# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    acs_cee_account_id = fields.Many2one("account.account", "Compte comptable de contribution environnementale")
    ad_montant_cee = fields.Float("Taux contribution environnementale")
    acs_rg_account_id = fields.Many2one("account.account", "Compte comptable de contribution énergétique")
    ad_montant_rg = fields.Float("Taux contribution énergétique")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
