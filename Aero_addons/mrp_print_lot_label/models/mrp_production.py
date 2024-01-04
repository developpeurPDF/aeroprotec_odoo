# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError

class MrpProduction(models.Model):
    _inherit = "mrp.production"

#    @api.multi #odoo13
    def action_print_lot_label(self):
        self.ensure_one()

        if not self.move_raw_ids and not self.finished_move_line_ids:
            raise ValidationError(_('No lot to print!'))

        active_ids = self.ids
        active_model = 'mrp.production'
        context = {
            'active_ids': active_ids,
            'active_model': active_model,
        }
        data = {}
        return self.env.ref(
            'mrp_print_lot_label.action_report_lot_label_workorder'
        ).with_context(context).report_action([], data=data)
