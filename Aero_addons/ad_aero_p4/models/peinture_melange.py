from odoo import api, fields, models, tools
from datetime import datetime


class PeintureMelange(models.Model):
    _name = 'peinture.melange'
    _description = 'Peinture et mélange peinture'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nom", readonly=True, copy=False, tracking=True)
    date = fields.Datetime("Date", tracking=True)
    sequence_lot_peinture = fields.Char("N° Sequence", readonly=True, copy=False, tracking=True)
    #lot_base = fields.Char("Base du lot", tracking=True)
    #lot_durcisseur = fields.Char("Lot Durcisseur", tracking=True)
    #lot_diluant = fields.Char("Lot Diluant", tracking=True)
    diluant = fields.Many2one('product.template', string="Diluant", tracking=True, domain="[('diluant', '=', True)]")
    base = fields.Many2one('product.template', string="Base", tracking=True, domain="[('base', '=', True)]")
    durcisseur = fields.Many2one('product.template', string="Durcisseur", tracking=True, domain="[('durcisseur', '=', True)]")
    lot_diluant = fields.Many2one(
    'stock.lot',
    string="Lot Diluant",
    tracking=True,
    domain="[('product_id.product_tmpl_id', '=', diluant)]"
    )
    lot_base = fields.Many2one('stock.lot', string="Base du lot", tracking=True, domain="[('product_id.product_tmpl_id', '=', base)]")
    lot_durcisseur = fields.Many2one('stock.lot', string="Lot Durcisseur", tracking=True, domain="[('product_id.product_tmpl_id', '=', durcisseur)]")
    #lot_base = fields.Many2one('stock.lot', string="Base du lot", tracking=True, related="base.name")
    #lot_durcisseur = fields.Many2one('stock.lot', string="Lot Durcisseur", tracking=True, related="durcisseur.name")
    #lot_diluant = fields.Many2one('stock.lot', string="Lot Diluant", tracking=True, domain="[('product_id.product_tmpl_id.diluant', '=', True)]")
    lot_base = fields.Many2one('stock.lot', string="Base du lot", tracking=True, domain="[('product_id.product_tmpl_id.base', '=', True)]")
    lot_durcisseur = fields.Many2one('stock.lot', string="Lot Durcisseur", tracking=True, domain="[('product_id.product_tmpl_id.durcisseur', '=', True)]")
    Temperature = fields.Char("Température", tracking=True)
    hygrometrie = fields.Char("Hygrometrie", tracking=True)
    viscosite = fields.Char("Viscosité", tracking=True)
    date_fabrication = fields.Datetime("Date de fabrication", tracking=True)

    @api.model
    def create(self, vals):

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        if current_month == 12:
            next_year = current_year + 1
            next_month = 1
        else:
            next_year = current_year
            next_month = current_month + 1

        count = self.env['peinture.melange'].search_count([
            ('create_date', '>=', f'{current_year}-{current_month:02d}-01'),
            ('create_date', '<', f'{next_year}-{next_month:02d}-01')
        ]) + 1

        sequence_melange = f"MP/{current_year}/{current_month:02d}/{count:03d}"
        vals['sequence_lot_peinture'] = sequence_melange

        vals['name'] = sequence_melange
        

        return super(PeintureMelange, self).create(vals)



