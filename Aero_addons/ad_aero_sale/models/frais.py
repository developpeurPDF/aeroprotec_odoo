# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Frais(models.Model):
    _name = "frais"

    name = fields.Char("Nom du frais")
    type_frais = fields.Selection(selection=[
            ('percentage','Pourcentage'),
            ('fixed','Fixé')],
        string='Type de frais')
    amount = fields.Float("Montant")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    priorite = fields.Selection(selection=[
        ('oui', 'Oui'),
        ('non', 'Non')],
        string='Priorité')
    frais_article = fields.Boolean("Frais article", default=False)
    frais_client = fields.Boolean("Frais client", default=False)
    frais_facturation = fields.Boolean("Frais facturation", default=False)
    a_la_commande = fields.Boolean("A la commande", default=False)
    a_la_commande_amount = fields.Float("Montant de frais à la commande")
    seuil_a_la_ligne = fields.Boolean("Seuil à la ligne", default=False)
    seuil_a_la_ligne_amount = fields.Float("Montant frais de seuil à la ligne")
    minimum_mensuel = fields.Boolean("Minimum", default=False)
    minimum_mensuel_amount = fields.Float("Montant de frais de minimum mensuel")
