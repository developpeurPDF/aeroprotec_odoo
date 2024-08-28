from odoo import api, fields, models, _
from odoo.exceptions import UserError


class cont_envCEE(models.Model):
    _name = 'contribution.environnementale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Contribution environnementale'

    name = fields.Char('Contribution environnementale')
    invoice_number = fields.Char('Numéro de la facture')
    customer_id = fields.Many2one('res.partner', 'Client')
    amount = fields.Float('Montant')
    due_date = fields.Date("Date d'échance")
    invoice_date = fields.Date("Date de la facture")
    move_id = fields.Many2one('account.move', 'Facture de débours')
    origin_move_id = fields.Many2one('account.move', "Facture d'origine")
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('invoiced', 'Facturé'),
        ],
        string='Status',
        copy=False,
        tracking=True, 
        default='draft',
    )
    account_id = fields.Many2one(
        comodel_name='account.account', string="Compte"
    )
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', ondelete='restrict',
        string='Company', default=lambda self: self.env.company)

    def action_confirm(self):
        if self.name == _('New'):
            self.name = self.env['ir.sequence'].next_by_code('seq.cont_env.cee') or _('New')
        self.write({'state': 'confirmed'})

    def reset_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def create_invoice(self):
        product_cont_env_energie = self.env.ref('ad_taux_contribution.product_cont_env_energie')
        product_cont_env_cee = self.env.ref('ad_taux_contribution.product_cont_env_cee')

        selected_records = self.env['contribution.environnementale'].browse(self.env.context.get('active_ids'))
        records_by_customer = {}
        if not selected_records:
            if self.id:
                selected_records = self
        for record in selected_records:
            if record.customer_id in records_by_customer:
                records_by_customer[record.customer_id].append(record)
            else:
                records_by_customer[record.customer_id] = [record]
        invoices = []
        for customer, records in records_by_customer.items():
            invoice_lines = []
            for record in records:
                if not record.state == 'invoiced':
                    invoice_lines.append((0, 0,
                                          {
                                              # 'product_id': product_cont_env_energie.id,
                                              'name': 'cont_env Energie',
                                              # 'account_id': record.account_id.id,
                                              'quantity': 1.0, 'price_unit': 17.5, 'tax_ids': False,
                                              'price_subtotal': 0.0,
                                              'currency_id': record.account_id.company_id.currency_id.id}))
                    # invoice_lines.append((0, 0, {
                    #     # 'product_id': product_cont_env_energie.id,
                    #     'name': product_cont_env_energie.description,
                    #     'debit': 17.5,
                    #     'credit': 17.5,
                    #     'account_id': record.account_id.id,
                    #     'tax_ids': [],
                    # }))
                    invoice_lines.append((0, 0,
                                          {
                                              # 'product_id': product_cont_env_cee.id,
                                              'name': 'Contribution environnementale',
                                              # 'account_id': record.account_id.id,
                                              'quantity': 1.0, 'price_unit': record.amount, 'tax_ids': False,
                                              'price_subtotal': 0.0,
                                              'currency_id': record.account_id.company_id.currency_id.id}))
                    # invoice_lines.append((0, 0, {
                    #     # 'product_id': product_cont_env_cee.id,
                    #     'name': product_cont_env_cee.description,
                    #     'debit': record.amount,
                    #     'credit': record.amount,
                    #     'account_id': record.account_id.id,
                    #     'tax_ids': [],
                    # }))

            if invoice_lines:
                invoice = self.env['account.move'].create({
                    'partner_id': customer.id,
                    'move_type': 'out_invoice',
                    'invoice_line_ids': invoice_lines,
                })
                invoices.append(invoice)
                for record in records:
                    record.move_id = invoice.id
                    record.state = 'invoiced'
            else:
                raise UserError(
                    _("Il n'y a pas de lignes à facturer"))
        # Return the action to open the invoices
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices[0].id
        else:
            action['domain'] = [('id', 'in', [invoice.id for invoice in invoices])]
        return action
