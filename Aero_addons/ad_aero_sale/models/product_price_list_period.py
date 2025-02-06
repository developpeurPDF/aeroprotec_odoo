from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class ProductPricelistPeriod(models.Model):
    _name = 'product.pricelist.period'
    _description = 'Pricing based on specific periods'

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', required=True, ondelete='cascade')
    prix = fields.Float(string='Prix', required=True)
    date_debut = fields.Date(string='Date de début', required=True)
    date_fin = fields.Date(string='Date de fin', required=True)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pricelist_period_ids = fields.One2many('product.pricelist.period', 'product_tmpl_id', string='Price Periods',compute="_compute_pricelist_periods")
    price = fields.Float("price")
    list_price = fields.Float(
        'Sales Price', default=0,
        digits='Product Price',
        help="Price at which the product is sold to customers.",
        compute="_check_current_price_period", readonly=False,)

    marge_price_from_cost = fields.Float(string="Coef Marge", )
    price_from_cost = fields.Float(string="Prix selon coût de revient", compute="_compute_price_from_cost")

    @api.depends('marge_price_from_cost', 'standard_price')
    def _compute_price_from_cost(self):
        for rec in self:
            rec.price_from_cost = rec.marge_price_from_cost * rec.standard_price


    @api.depends('order_line_ids')
    def _compute_pricelist_periods(self):
        for rec in self:
            # Supprimez les anciennes périodes de prix
            rec.pricelist_period_ids.unlink()

            # Création des nouvelles périodes de prix
            for line in rec.order_line_ids:
                if line.order_id.state == 'devis_validee':
                    price_unit = line.price_unit
                    date_debut = line.order_id.date_order
                    date_fin = line.order_id.validity_date  # Date d'expiration
                    validite_prix_vente = rec.client.validite_prix_vente or 12
                    # Création d'un enregistrement dans le modèle product.pricelist.period
                    self.env['product.pricelist.period'].create({
                        'product_tmpl_id': rec.id,
                        'prix': price_unit,
                        'date_debut': date_debut,
                        'date_fin': date_debut + relativedelta(months=validite_prix_vente),
                    })

    @api.depends('pricelist_period_ids', 'price_from_cost')
    def _check_current_price_period(self):
        today = date.today()
        for product in self:
            price_found = False
            for period in product.pricelist_period_ids:
                if period.date_debut <= today <= period.date_fin:
                    if product.list_price != period.prix:
                        product.list_price = period.prix
                    price_found = True
                    break

            if not price_found:
                product.list_price = product.price_from_cost



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float(
            string="Unit Price",
            compute='_compute_price_unit',
            digits='Product Price',
            store=True, readonly=False, required=True, precompute=True, default=0)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    validite_prix_vente = fields.Integer(string="Validité prix vente")