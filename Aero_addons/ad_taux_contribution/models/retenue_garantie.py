from odoo import api, fields, models, _


class RetenueGarantie(models.Model):
    _name = 'sf.retenue.guarantee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Contribution énergétique'
    _order = 'id desc'

    name = fields.Char('Retenue de ganatie', copy=False, default=lambda self: _('Retention Number'))
    invoice_number = fields.Char('Numéro de la facture')
    customer_id = fields.Many2one('res.partner', 'Client')
    amount = fields.Float('Montant')
    due_date = fields.Date("Date d'échance (RG)")
    invoice_date = fields.Date("Date de la facture")
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        copy=False,
        tracking=True,
        default='draft',
    )
    invoice_date = fields.Date("Date de la facture")
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', ondelete='restrict',
        string='Company', default=lambda self: self.env.company)

    def action_confirm(self):
        for rec in self:
            if rec.name in [_('Retention Number'),_('New')]:
                rec.name = self.env['ir.sequence'].next_by_code('seq.retenue.guarantee') or _('New')
            rec.write({'state': 'confirmed'})
    
    def action_paid(self):
        self.write({'state': 'paid'})

    def reset_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
