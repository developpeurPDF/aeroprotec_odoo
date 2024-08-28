# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Contact(models.Model):
    _inherit = "res.partner"

    appliquer_seuil_a_la_ligne = fields.Boolean(string="Appliquer la seuil à la ligne de commande")
    seuil_a_la_ligne = fields.Float(string="Seuil à la ligne de commande", readonly=False)

    state = fields.Selection([
        ('normal', 'Normal'),
        ('warning', 'Alerte'),
        ('block', 'Bloqué')], compute='_compute_contact_state', default='normal')
    edi = fields.Char("Identifiant EDI")
    code_abreviation = fields.Char("Code abréviation client")
    client_factor = fields.Selection(selection=[
            ('oui','Oui'),
            ('non','Non')],
        string='Client FACTOR',tracking=True)
    client_franco = fields.Selection(selection=[
        ('oui', 'Oui'),
        ('non', 'Non')],
        string='Client Franco de port', tracking=True)
    # type_contact = fields.Selection(selection=[
    #     ('prospect', 'Prospect'),
    #     ('client', 'Client'),
    #     ('employee', 'Employee'),
    #     ('autre', 'Autre'), ],
    #     string='Type du contact', default='prospect', compute='_compute_contact_type',)
    prospect = fields.Boolean("Prospect", compute='_compute_prospect', default=True)

    frais = fields.Many2many('frais',
                             string="Frais", readonly=False, domain= "[('frais_facturation', '!=', 'oui'), ('frais_article', '!=', 'oui'),]",)



    def _compute_contact_state(self):
        for rec in self:
            if rec.sale_warn == "block" or rec.purchase_warn == "block" or rec.invoice_warn == "block" or rec.picking_warn == "block":
                rec.state = "block"
            elif rec.sale_warn == "warning" or rec.purchase_warn == "warning" or rec.invoice_warn == "warning" or rec.picking_warn == "warning":
                rec.state = "warning"
            else:
                rec.state = "normal"

    def _compute_prospect(self):
        for rec in self:
            if rec.total_invoiced > 0:
                rec.prospect = False
            else:
                rec.prospect = True

