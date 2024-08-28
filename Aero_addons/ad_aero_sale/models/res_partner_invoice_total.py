from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class PartnerInvoiceTotal(models.Model):
    _name = 'res.partner.invoice.total'
    _description = 'Monthly Invoice Total for Partner'

    partner_id = fields.Many2one('res.partner', string='Client', required=True, ondelete='cascade')
    month_year = fields.Char(string='Mois-Année', required=True)
    total_amount = fields.Float(string='Montant Total', required=True)

    @api.model
    def create_monthly_totals(self):
        today = fields.Date.today()
        start_date = today.replace(day=1).replace(month=1)  # Start of the year
        current_month = today.replace(day=1)

        partners = self.env['res.partner'].search([])

        for partner in partners:
            date_pointer = start_date
            while date_pointer <= current_month:
                end_date = date_pointer + relativedelta(months=1, days=-1)
                moves = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('move_type', '=', 'out_invoice'),
                    ('invoice_date', '>=', date_pointer),
                    ('invoice_date', '<=', end_date),
                    ('state', '=', 'posted')  # Only consider confirmed invoices
                ])

                total_amount = 0.0
                for move in moves:
                    for line in move.invoice_line_ids:
                        if not line.product_id.type_frais:
                            total_amount += line.price_subtotal  # Subtotal is the amount without taxes

                month_year_str = date_pointer.strftime('%m-%Y')
                existing_record = self.search([('partner_id', '=', partner.id), ('month_year', '=', month_year_str)])
                if existing_record:
                    existing_record.write({'total_amount': total_amount})
                else:
                    self.create({
                        'partner_id': partner.id,
                        'month_year': month_year_str,
                        'total_amount': total_amount
                    })

                date_pointer += relativedelta(months=1)

