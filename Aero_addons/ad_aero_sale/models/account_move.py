from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if move.move_type == 'out_invoice' and move.state == 'posted':
            move.partner_id._update_invoice_totals(move.invoice_date)
        return move

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'state' in vals and vals['state'] == 'posted':
            for move in self:
                if move.move_type == 'out_invoice':
                    move.partner_id._update_invoice_totals(move.invoice_date)
        return res
