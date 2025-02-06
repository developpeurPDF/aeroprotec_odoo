# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta


class Contact(models.Model):
    _inherit = "res.partner"

    appliquer_seuil_a_la_ligne = fields.Boolean(string="Appliquer le seuil à la ligne de commande")
    seuil_a_la_ligne = fields.Float(string="Seuil à la ligne de commande", readonly=False)
    modes_reglement = fields.Many2one('modes.reglement', string="Mode de réglement")
    invoice_totals = fields.One2many('res.partner.invoice.total', 'partner_id', string='Total Facture')
    appliquer_mini_facturation = fields.Boolean(string="Appliquer le minimum de facturation")
    mini_facturation = fields.Float(string="Montant de minimum de facturation", readonly=False)
    invoice_total_count = fields.Integer(string='Invoice Totals', compute='_compute_invoice_total_count')
    address_facturation_par_defaut = fields.Boolean(string='Adresse de facturation par défaut',)
    address_livraison_par_defaut = fields.Boolean(string='Adresse de livraison par défaut',)
    contact_supply = fields.Many2one('res.partner', string="Contact Supply")
    bl_to_fact = fields.Boolean(string="1 BL = 1 Facture")
    xfact_to_bl = fields.Boolean(string="X BL = 1 Facture")


    def _check_and_create_minimum_billing(self):
        today = fields.Date.today()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - relativedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        for partner in self.search([('appliquer_mini_facturation', '=', True)]):
            invoice_total_record = self.env['res.partner.invoice.total'].search([
                ('partner_id', '=', partner.id),
                ('month_year', '=', first_day_of_previous_month.strftime('%m-%Y'))
            ], limit=1)

            total_amount = invoice_total_record.total_amount if invoice_total_record else 0.0

            if total_amount < partner.mini_facturation:
                difference = partner.mini_facturation - total_amount
                invoice_vals = {
                    'partner_id': partner.id,
                    'move_type': 'out_invoice',
                    'invoice_date': today,
                    'invoice_line_ids': [(0, 0, {
                        'name': 'Ajustement de facturation minimum',
                        'quantity': 1,
                        'price_unit': difference,
                    })],

                }
                if partner.company_id:
                    invoice_vals['company_id'] = partner.company_id.id
                self.env['account.move'].create(invoice_vals)

    def _compute_invoice_total_count(self):
        for partner in self:
            partner.invoice_total_count = self.env['res.partner.invoice.total'].search_count(
                [('partner_id', '=', partner.id)])

    def action_open_invoice_totals(self):
        return {
            'name': 'Invoice Totals',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner.invoice.total',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def _update_invoice_totals(self, invoice_date):
        month_start = invoice_date.replace(day=1)
        month_end = month_start + relativedelta(months=1, days=-1)
        month_year_str = month_start.strftime('%m-%Y')

        for partner in self:
            moves = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', month_start),
                ('invoice_date', '<=', month_end),
                ('state', '=', 'posted')
            ])

            total_amount = 0.0
            for move in moves:
                for line in move.invoice_line_ids:
                    if not line.product_id.type_frais:
                        total_amount += line.price_subtotal  # Subtotal is the amount without taxes

            existing_record = self.env['res.partner.invoice.total'].search([
                ('partner_id', '=', partner.id),
                ('month_year', '=', month_year_str)
            ])

            if existing_record:
                existing_record.write({'total_amount': total_amount})
            else:
                self.env['res.partner.invoice.total'].create({
                    'partner_id': partner.id,
                    'month_year': month_year_str,
                    'total_amount': total_amount
                })

    state = fields.Selection([
        ('normal', 'Normal'),
        ('warning', 'Alerte'),
        ('block', 'Bloqué')], compute='_compute_contact_state', default='normal')
    edi = fields.Char("Identifiant EDI")
    code_abreviation = fields.Char("Code abréviation client")
    client_factor = fields.Selection(selection=[
            ('oui','Oui'),
            ('non','Non')],
        string='Client FACTOR',tracking=True, default='non')
    # partner_invoice_id = fields.Many2one("res.partner", string='Adresse de facturation', tracking=True)
    # type_contact = fields.Selection(selection=[
    #     ('prospect', 'Prospect'),
    #     ('client', 'Client'),
    #     ('employee', 'Employee'),
    #     ('autre', 'Autre'), ],
    #     string='Type du contact', default='prospect', compute='_compute_contact_type',)
    prospect = fields.Boolean("Prospect", compute='_compute_prospect', default=True)

    # frais = fields.Many2many('frais',
    #                          string="Frais", readonly=False, domain= "[('frais_facturation', '!=', 'oui'), ('frais_article', '!=', 'oui'),]",)

    frais = fields.Many2many('account.tax',
                             string="Frais Client", readonly=False, domain="[('frais', '=', True)]", )
    frais_fai = fields.Many2one('account.tax', string="Frais FAI", readonly=False, domain="[('frais', '=', True)]", )
    frais_lancement = fields.Many2one('account.tax', string="Frais Lancement", readonly=False, domain="[('frais', '=', True)]", )
    product_fees_ids = fields.One2many('partner.product.fees', 'partner_id', string='Frais')




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

    product_ids = fields.One2many('product.template', 'client', string="Produits")
    total_frais = fields.Many2many('account.tax', string="Frais Associés", compute='_compute_total_frais')
    product_id = fields.One2many('product.template', 'frais', string="Frais associés")

    @api.depends('product_ids.frais')
    def _compute_total_frais(self):
        for partner in self:
            all_frais = self.env['account.tax']
            for product in partner.product_ids:
                all_frais |= product.frais
            partner.total_frais = all_frais

    # product_seuil_info = fields.Text(string="Liste des Produits et Montant de Seuil",
    #                                  compute='_compute_product_seuil_info')
    #
    # @api.depends('product_ids')
    # def _compute_product_seuil_info(self):
    #     for partner in self:
    #         info = ""
    #         for product in partner.product_ids:
    #             info += f"Produit: {product.name}, Montant de Seuil: {product.montant_seuil_a_la_commande}\n"
    #         partner.product_seuil_info = info




# class ProductSeuilInfo(models.Model):
#     _name = 'product.seuil.info'
#     _description = 'Informations des Produits et Montant de Seuil'
#
#     partner_id = fields.Many2one('res.partner', string="Partenaire")
#     product_id = fields.Many2one('product.template', string="Produit")
#     montant_seuil = fields.Float(string="Montant de Seuil")