from odoo import api, models, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    is_pick_stock = fields.Boolean("is pick stock", default=False, readonly=True, copy=False)
    is_pack_stock = fields.Boolean("is pack stock", default=False, readonly=True, copy=False)

    def _create_backorder(self):
        backorders = super(Picking, self)._create_backorder()
        for bo in backorders:
            bo.is_pick_stock = bo.backorder_id.is_pick_stock
            bo.is_pack_stock = bo.backorder_id.is_pack_stock

        return backorders


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_state = fields.Selection([
        ('partial_ready', 'Partial Ready'),
        ('fully_ready', 'Fully Ready'),
        ('waiting', 'Waiting'), ('overdue', 'Overdue'),
        ('pick_stock', 'Pick Stock'),
        ('pack_stock', 'Pack Stock'),
        ('partial_delivery', 'Partial Delivered'),
        ('fully_delivery', 'Fully Delivered')], string='Delivery Status',
        copy=False, default=False, index=True, readonly=False,
        help="Delivery Status.")

    compute_delivery_state = fields.Char(string='Delivery Status', compute='_calculate_delivery_state', store=False,
                                        copy=False, default='waiting', index=True, readonly=True,
                                        help="Delivery Status.")

    ribbon_delivery_state = fields.Char(string='Delivery Status', default='', compute='_calculate_delivery_state')

    compute_field = fields.Boolean(compute='_check_group_user')

    def _calculate_delivery_state(self):
        for p in self:
            if p.state in ['sale', 'done']:
                delivery_steps = p.warehouse_id.delivery_steps
                if delivery_steps == 'ship_only':
                    p._delivery_ship_only()
                elif delivery_steps == 'pick_ship':
                    p._delivery_pick_ship()
                elif delivery_steps == 'pick_pack_ship':
                    p._delivery_pick_pack_ship()


                commitment_date = p.commitment_date or p.expected_date

                # Check overdue
                if p.compute_delivery_state in ['waiting', 'partial_delivery'] and commitment_date:
                    today = fields.Date.context_today(self)
                    if commitment_date.date() < today:
                        p.compute_delivery_state = 'overdue'

                p.ribbon_delivery_state = p.compute_delivery_state
                if p.compute_delivery_state != p.delivery_state:
                    p.delivery_state = p.compute_delivery_state

                if p.compute_delivery_state == 'waiting':
                    p.compute_delivery_state = 'Waiting'
                elif p.compute_delivery_state == 'partial_ready':
                    p.compute_delivery_state = 'Partial Ready'
                elif p.compute_delivery_state == 'fully_ready':
                    p.compute_delivery_state = 'Fully Ready'
                elif p.compute_delivery_state == 'partial_delivery':
                    p.compute_delivery_state = 'Partial Delivered'
                elif p.compute_delivery_state == 'pick_stock':
                    p.compute_delivery_state = 'Pick Stock'
                elif p.compute_delivery_state == 'pack_stock':
                    p.compute_delivery_state = 'Pack Stock'
                elif p.compute_delivery_state == 'fully_delivery':
                    p.compute_delivery_state = 'Fully Delivered'
                elif p.compute_delivery_state == 'overdue' and commitment_date:
                    today = fields.Date.context_today(self)
                    diff = (today - commitment_date.date()).days
                    if diff == 1:
                        p.compute_delivery_state = 'Overdue (yesterday)'
                    elif diff > 1:
                        p.compute_delivery_state = 'Overdue (%s days ago)' % str(diff)

            else:
                p.compute_delivery_state = ''
                p.ribbon_delivery_state = ''

    def _delivery_ship_only(self):
        self.compute_delivery_state = 'waiting'

        pickings_done = self.picking_ids.filtered(lambda p: (p.state in ['done']))
        backorder_ids = pickings_done.backorder_ids.filtered(
            lambda p: (
                    p.state in ['waiting', 'confirmed', 'assigned']
            )
        )

        stock_move_done = pickings_done.move_ids_without_package.filtered(
            lambda sm: (
                    sm.sale_line_id
                    and sm.quantity_done == sm.sale_line_id.product_uom_qty
                    and sm.state in ['done']
            )
        )

        show_check_availability = self.picking_ids.filtered(lambda p: p.show_check_availability and p.state not in ['cancel','waiting'])
        assigned_picking = self.picking_ids.filtered(lambda p: (p.state in ['assigned']))

        if show_check_availability and assigned_picking:
            self.compute_delivery_state = 'partial_ready'
        elif not show_check_availability and assigned_picking:
            self.compute_delivery_state = 'fully_ready'

        elif len(self.order_line) <= len(stock_move_done):
            self.compute_delivery_state = 'fully_delivery'
        else:
            if backorder_ids:
                self.compute_delivery_state = 'partial_delivery'
            elif pickings_done and not self.picking_ids.filtered(lambda p: (p.state in ['assigned'])):
                self.compute_delivery_state = 'fully_delivery'
            elif pickings_done and self.picking_ids.filtered(lambda p: (p.state in ['assigned'])):
                self.compute_delivery_state = 'partial_delivery'

    def _delivery_pick_ship(self):
        self._delivery_ship_only()

        if self.compute_delivery_state in ['partial_delivery', 'fully_delivery', 'partial_ready', 'fully_ready']:
            group_pickings = self.env['stock.picking'].search([('group_id', '=', self.picking_ids.group_id.id),
                                                               ('state', '!=', 'cancel')])

            pick_assigned = group_pickings.filtered(lambda p: (p.state in ['assigned']
                                                               and p.is_pick_stock))
            if pick_assigned:
                self.compute_delivery_state = 'pick_stock'

    def _delivery_pick_pack_ship(self):
        self._delivery_ship_only()
        if self.compute_delivery_state in ['partial_delivery', 'fully_delivery', 'partial_ready', 'fully_ready']:

            group_pickings = self.env['stock.picking'].search([('group_id', '=', self.picking_ids.group_id.id),
                                                               ('state', '!=', 'cancel')])

            pick_assigned = group_pickings.filtered(lambda p: (p.state in ['assigned']
                                                                and p.is_pick_stock))

            pack_assigned = group_pickings.filtered(lambda p: (p.state in ['assigned']
                                                                  and p.is_pack_stock))

            if pick_assigned:
                self.compute_delivery_state = 'pick_stock'
            if not pick_assigned and pack_assigned:
                self.compute_delivery_state = 'pack_stock'


    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        group_pickings = self.env['stock.picking'].search([('group_id', '=', self.picking_ids.group_id.id),
                                                           ('state', '=', 'waiting')], order='id asc')

        if self.warehouse_id.delivery_steps == 'pick_ship' and len(group_pickings) == 1:
            p0 = group_pickings[0]
            p0.is_pick_stock = True
        elif self.warehouse_id.delivery_steps == 'pick_pack_ship' and len(group_pickings) == 2:
            p0 = group_pickings[0]
            p1 = group_pickings[1]
            if not p0.move_ids.move_dest_ids and p1.move_ids.move_dest_ids.ids == p0.move_ids.ids:
                p0.is_pack_stock = True
                p1.is_pick_stock = True

            if not p1.move_ids.move_dest_ids and p0.move_ids.move_dest_ids.ids == p1.move_ids.ids:
                p1.is_pack_stock = True
                p0.is_pick_stock = True

        return res

    def _check_group_user(self):
        for order in self:
            if self.env.user.has_group("sale_order_delivery_status.edit_delivery_status_manually"):
                order.compute_field = True
            else:
                order.compute_field = False
