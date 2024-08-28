
from odoo import models

class StockQuant(models.Model):
    _inherit = "stock.quant"

    # If product is available for picking. The Picking will be assigned with date_deadline priority
    def action_apply_inventory(self):
        super(StockQuant, self).action_apply_inventory()
        for quant in self:
            available_qty = self.env['stock.quant']._get_available_quantity(quant.product_id,
                                                                            quant.location_id)
            if available_qty:
                domain = [('product_id', '=', quant.product_id.id),
                          ('location_id', '=', quant.location_id.id),
                          ('state', 'in', ['draft', 'waiting', 'confirmed', 'partially_available', 'assigned'])]

                moves = self.env['stock.move'].search(domain, order='priority DESC, date_deadline asc')
                for move in moves:
                    available_qty = self.env['stock.quant']._get_available_quantity(quant.product_id,
                                                                                    quant.location_id)
                    if available_qty and move.picking_id and move.picking_id.picking_type_id.code in ['outgoing', 'internal']:
                        if move.picking_id.state == 'draft':
                            move.picking_id.action_confirm()
                            if move.picking_id.show_check_availability:
                                move.picking_id.action_assign()

                        elif move.picking_id.show_check_availability:
                            move.picking_id.action_assign()
                    if not available_qty:
                        break
