from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_order_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        compute='_compute_sale_order_lines',
        string="Lignes de commande liées"
    )

    @api.depends('sale_id')
    def _compute_sale_order_lines(self):
        for picking in self:
            if picking.sale_id:
                picking.sale_order_line_ids = picking.sale_id.order_line
            else:
                picking.sale_order_line_ids = False

    poids_carbone_total_liv = fields.Float("Poids Carbone Total", compute="_compute_poids_carbone_total_liv")

    @api.depends('sale_id', 'sale_order_line_ids.product_uom_qty')
    def _compute_poids_carbone_total_liv(self):
        for picking in self:
            total = 0.0
            if picking.sale_id:
                poids_carbone_unit = picking.sale_id.poids_carbone_unit or 0.0
                for line in picking.sale_order_line_ids:
                    total += poids_carbone_unit * line.product_uom_qty
            picking.poids_carbone_total_liv = total
