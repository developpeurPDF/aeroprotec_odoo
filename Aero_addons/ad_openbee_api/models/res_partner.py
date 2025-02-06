from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    openbee_folder_invoice_id = fields.Char(string="Dossier des factures", help="Dossier où stocker les documents des factures de ce partenaire")
    openbee_folder_sale_id = fields.Char(string="Dossier des commandes ventes", help="Dossier où stocker les documents des commandes ventes de ce partenaire")
    openbee_folder_purchase_id = fields.Char(string="Dossier des commandes achats", help="Dossier où stocker les documents des commandes achats de ce partenaire")
