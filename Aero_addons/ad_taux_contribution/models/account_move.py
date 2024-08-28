from odoo import api, fields, models, _
from odoo.tools import formatLang
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta


import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    guarantee_percentage_amount = fields.Float(compute='compute_guarantee_percentage_amount')
    sale_order_id = fields.Many2one('sale.order')
    guarantee_return = fields.Boolean(string="Contribution énergétique")
    rg_percentage = fields.Float('Taux de Contribution énergétique')
    date_echeance = fields.Date("Date d'échéance",  readonly=False) #compute='compute_date_echeance',
    prime_total_amount = fields.Float(compute='compute_prime_percentage')
    prime_amount = fields.Float("Taux de Contribution environnementale")
    prime = fields.Boolean(string="Contribution environnementale")
    invoice_line_ids = fields.One2many(domain=lambda self: self._domain_invoice_line_ids())

    @api.model
    def _domain_invoice_line_ids(self):
        company = self.company_id or self.env.company
        account_id = company.acs_cee_account_id
        rg_account_id = company.acs_rg_account_id
        res = [('account_id', 'not in', (account_id.id, rg_account_id.id)),
               ('display_type', 'in', ('product', 'line_section', 'line_note'))]
        return res

    @api.depends('amount_total', 'prime_amount')
    def compute_prime_percentage(self):
        for rec in self:
            rec.prime_total_amount = rec.amount_total - rec.prime_amount

    @api.depends('amount_total', 'rg_percentage')
    def compute_guarantee_percentage_amount(self):
        for rec in self:
            total_credit = sum([aml.credit for aml in rec.line_ids])
            rec.guarantee_percentage_amount = total_credit * (rec.rg_percentage / 100)

    # def compute_date_echeance(self):
    #     for rec in self:
    #         rec.date_echeance = fields.Date.context_today(self).replace(fields.Date.context_today(self).year + 1)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get('is_payment'):
            return res

        rg_account_id = self.env.company.acs_rg_account_id
        rg_product_id = self.env['product.product'].search([('property_account_income_id', '=', rg_account_id.id)])
        account_id = self.env.company.acs_cee_account_id
        product_id = self.env['product.product'].search([('property_account_income_id', '=', account_id.id)])
        currency_id = account_id.company_id.currency_id
        if res.get('move_type')=='out_invoice':
            line_ids = []
            if rg_account_id:
                line_ids.append(
                    (0, 0, {'product_id': rg_product_id.id, 'name': 'RG', 'account_id': rg_account_id.id,
                            'quantity': 1.0, 'price_unit': 0.0, 'tax_ids': False,
                            'price_subtotal': 0.0, 'currency_id': currency_id.id, 'acs_is_rg_line': True, 'display_type': 'product'}))
            if account_id:
                line_ids.append(
                    (0, 0, {'product_id': product_id.id, 'name': 'Contribution environnementale', 'account_id': account_id.id,
                            'quantity': 1.0, 'price_unit': 0.0, 'tax_ids': False,
                            'price_subtotal': 0.0, 'currency_id': currency_id.id, 'acs_is_rg_line': True, 'display_type': 'product'}))
            if line_ids:
                res['line_ids'] = line_ids
        return res

    @api.onchange('line_ids')
    def onchange_move_lines_rg(self):
        for rec in self:
            rg_account_id = rec.company_id.acs_rg_account_id
            rg_line_id = rec.line_ids.filtered(lambda line: line.account_id.id == rg_account_id.id)
            if rg_account_id and rg_line_id:
                if rec.guarantee_return:
                    rg_line_id.price_unit = -(rec.guarantee_percentage_amount)
                else:
                    rg_line_id.price_unit = 0
            account_id = rec.company_id.acs_cee_account_id
            line_id = rec.line_ids.filtered(lambda line: line.account_id.id == account_id.id)
            if account_id and line_id:
                if rec.prime:
                    line_id.price_unit = -rec.prime_amount
                else:
                    line_id.price_unit = 0

    @api.onchange('guarantee_return', 'rg_percentage', 'amount_total')
    def onchange_rg_ec(self):
        for rec in self:
            rg_account_id = rec.company_id.acs_rg_account_id
            if rec.guarantee_return and not rg_account_id:
                raise UserError(_("Please set Contribution environnementale & Contribution énergétique Accounts on company."))
            rg_line_id = rec.line_ids.filtered(lambda line: line.account_id.id == rg_account_id.id)
            if rg_account_id and rg_line_id:
                if rec.guarantee_return:
                    rg_line_id.price_unit = -(rec.guarantee_percentage_amount)
                else:
                    rg_line_id.price_unit = 0

    @api.onchange('prime_amount', 'prime', 'amount_total')
    def onchange_prime_ec(self):
        for rec in self:
            account_id = rec.company_id.acs_cee_account_id
            if rec.prime_amount and not account_id:
                raise UserError(_("Please set Contribution environnementale & Contribution énergétique Accounts on company."))

            line_id = rec.line_ids.filtered(lambda line: line.account_id.id == account_id.id)
            if account_id and line_id:
                if rec.prime:
                    line_id.price_unit = -(rec.prime_amount)
                else:
                    line_id.price_unit = 0

    def action_post(self):
        for record in self:
            if record.move_type == 'out_invoice':
                lines_to_remove = record.line_ids.filtered(lambda line: line.debit == 0.0 and line.credit == 0.0 and not line.move_id.state == 'posted')
                if lines_to_remove:
                    lines_to_remove.unlink()
        due_date = fields.Date.context_today(self) + timedelta(days=365)
        res = super(AccountMove, self).action_post()
        for record in self:
            if record.move_type == 'out_invoice':
                if record.guarantee_return:
                    vals = {
                        'name': _('Retention Number'),
                        'invoice_number': record.name,
                        'customer_id': record.partner_id.id,
                        'invoice_date': record.invoice_date,
                        'amount': record.guarantee_percentage_amount,
                        'due_date': due_date
                    }
                    guarantee = self.env['sf.retenue.guarantee'].create(vals)
                    guarantee.action_confirm()
                if record.prime:
                    account = record.company_id.acs_cee_account_id
                    vals_cee = {
                        'name': _('New'),
                        'invoice_number': record.name,
                        'origin_move_id': record.id,
                        'invoice_date': record.invoice_date,
                        'customer_id': record.partner_id.id,
                        'amount': record.prime_amount,
                        'due_date': record.invoice_date_due,
                        'account_id': account.id
                    }
                    rec = self.env['sf.prime.cee'].create(vals_cee)
                    if rec:
                        rec.action_confirm()
        return res

    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'guarantee_percentage_amount',
        'rg_percentage',
        'guarantee_return',
        'prime_amount',
        'prime')
    def _compute_tax_totals(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            extra_amount = 0
            if move.is_invoice(include_receipts=True):
                base_lines = move.line_ids.filtered(lambda line: line.display_type == 'product' and not line.acs_is_rg_line)
                base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]

                if move.id:
                    sign = -1 if move.is_inbound(include_receipts=True) else 1
                    base_line_values_list += [
                        {
                            **line._convert_to_tax_base_line_dict(),
                            'handle_price_include': False,
                            'quantity': 1.0,
                            'price_unit': sign * line.amount_currency,
                        }
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
                    ]

                kwargs = {
                    'base_lines': base_line_values_list,
                    'currency': move.currency_id or move.journal_id.currency_id or move.company_id.currency_id,
                }

                if move.id:
                    kwargs['tax_lines'] = [
                        line._convert_to_tax_line_dict()
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
                    ]
                else:
                    epd_aggregated_values = {}
                    for base_line in base_lines:
                        if not base_line.epd_needed:
                            continue
                        for grouping_dict, values in base_line.epd_needed.items():
                            epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
                            epd_values['price_subtotal'] += values['price_subtotal']

                    for grouping_dict, values in epd_aggregated_values.items():
                        taxes = None
                        if grouping_dict.get('tax_ids'):
                            taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

                        kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
                            None,
                            partner=move.partner_id,
                            currency=move.currency_id,
                            taxes=taxes,
                            price_unit=values['price_subtotal'],
                            quantity=1.0,
                            account=self.env['account.account'].browse(grouping_dict['account_id']),
                            analytic_distribution=values.get('analytic_distribution'),
                            price_subtotal=values['price_subtotal'],
                            is_refund=move.move_type in ('out_refund', 'in_refund'),
                            handle_price_include=False,
                        ))
                move.tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)
                rounding_line = move.line_ids.filtered(lambda l: l.display_type == 'rounding')
                if rounding_line:
                    amount_total_rounded = move.tax_totals['amount_total'] - rounding_line.balance
                    move.tax_totals['formatted_amount_total_rounded'] = formatLang(self.env, amount_total_rounded,
                                                                                   currency_obj=move.currency_id) or ''

                if move.prime and move.guarantee_return:
                    extra_amount = (move.prime_amount + move.guarantee_percentage_amount)
                    if move.tax_totals.get('subtotals'):
                        for subtotal in move.tax_totals['subtotals']:
                            if subtotal['name'] in ['Montant HT', 'Untaxed Amount']:
                                ut_amount = formatLang(self.env, subtotal['amount'], currency_obj=move.currency_id)
                                subtotal['formatted_amount'] = ut_amount
                                move.tax_totals['custom_untaxed_formatted_amount'] = ut_amount
                
                    move.tax_totals['untaxed_custom'] = formatLang(self.env, move.tax_totals['amount_untaxed'] + (move.prime_amount + move.guarantee_percentage_amount), currency_obj=move.currency_id)
                    move.tax_totals['prime_amount'] = move.prime_amount
                    
                    move.tax_totals['prime_amount_formatted'] = formatLang(self.env, move.prime_amount, currency_obj=move.currency_id)
                    move.tax_totals['guarantee_percentage_amount'] = move.guarantee_percentage_amount
                    move.tax_totals['rg_percentage'] = move.rg_percentage
                    move.tax_totals['guarantee_percentage_amount_formatted'] = formatLang(self.env, move.guarantee_percentage_amount, currency_obj=move.currency_id)
 
                elif move.prime:
                    extra_amount = move.prime_amount
                    if move.tax_totals.get('subtotals'):
                        for subtotal in move.tax_totals['subtotals']:
                            if subtotal['name'] in ['Montant HT', 'Untaxed Amount']:
                                ut_amount = formatLang(self.env, subtotal['amount'], currency_obj=move.currency_id)
                                subtotal['formatted_amount'] = ut_amount
                                move.tax_totals['custom_untaxed_formatted_amount'] = ut_amount
                    
                    move.tax_totals['untaxed_custom'] = formatLang(self.env, move.tax_totals['amount_untaxed'] + move.prime_amount, currency_obj=move.currency_id)
                    move.tax_totals['prime_amount'] = move.prime_amount
                    move.tax_totals['prime_amount_formatted'] = formatLang(self.env, move.prime_amount, currency_obj=move.currency_id)
                elif move.guarantee_return:
                    extra_amount = move.guarantee_percentage_amount
                    if move.tax_totals.get('subtotals'):
                        for subtotal in move.tax_totals['subtotals']:
                            if subtotal['name'] in ['Montant HT', 'Untaxed Amount']:
                                ut_amount = formatLang(self.env, subtotal['amount'], currency_obj=move.currency_id)
                                subtotal['formatted_amount'] = ut_amount
                                move.tax_totals['custom_untaxed_formatted_amount'] = ut_amount
                    
                    move.tax_totals['untaxed_custom'] = formatLang(self.env, move.tax_totals['amount_untaxed'] + extra_amount, currency_obj=move.currency_id)
                    move.tax_totals['guarantee_percentage_amount'] = extra_amount
                    move.tax_totals['rg_percentage'] = move.rg_percentage
                    move.tax_totals['guarantee_percentage_amount_formatted'] = formatLang(self.env, extra_amount, currency_obj=move.currency_id)
                print ("move.tax_totals---",move.tax_totals)
                move.tax_totals['custom'] = formatLang(self.env, move.tax_totals['amount_total'] - extra_amount, currency_obj=move.currency_id) 
            else:
                move.tax_totals = None


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    acs_is_rg_line = fields.Boolean("Is RG Line")

    @api.depends('balance', 'move_id.is_storno')
    def _compute_debit_credit(self):
        for line in self:
            if not line.is_storno:
                line.debit = line.balance if line.balance > 0.0 else 0.0
                line.credit = -line.balance if line.balance < 0.0 else 0.0
            else:
                line.debit = line.balance if line.balance < 0.0 else 0.0
                line.credit = -line.balance if line.balance > 0.0 else 0.0
    
    #ACS: Avoid validation for RG lines
    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            if line.move_id.is_sale_document(include_receipts=True):
                if ((line.display_type == 'payment_term') ^ (account_type == 'asset_receivable')) and not line.acs_is_rg_line:
                    raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
            if line.move_id.is_purchase_document(include_receipts=True):
                if ((line.display_type == 'payment_term') ^ (account_type == 'liability_payable')) and not line.acs_is_rg_line:
                    raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))

    #ACS: only avoid for frequent account.
    def _compute_account_id(self):
        term_lines = self.filtered(lambda line: line.display_type == 'payment_term')
        if term_lines:
            moves = term_lines.move_id
            self.env.cr.execute("""
                WITH previous AS (
                    SELECT DISTINCT ON (line.move_id)
                           'account.move' AS model,
                           line.move_id AS id,
                           NULL AS account_type,
                           line.account_id AS account_id
                      FROM account_move_line line
                     WHERE line.move_id = ANY(%(move_ids)s)
                       AND line.display_type = 'payment_term'
                       AND line.id != ANY(%(current_ids)s)
                ),
                properties AS(
                    SELECT DISTINCT ON (property.company_id, property.name, property.res_id)
                           'res.partner' AS model,
                           SPLIT_PART(property.res_id, ',', 2)::integer AS id,
                           CASE
                               WHEN property.name = 'property_account_receivable_id' THEN 'asset_receivable'
                               ELSE 'liability_payable'
                           END AS account_type,
                           SPLIT_PART(property.value_reference, ',', 2)::integer AS account_id
                      FROM ir_property property
                      JOIN res_company company ON property.company_id = company.id
                     WHERE property.name IN ('property_account_receivable_id', 'property_account_payable_id')
                       AND property.company_id = ANY(%(company_ids)s)
                       AND property.res_id = ANY(%(partners)s)
                  ORDER BY property.company_id, property.name, property.res_id, account_id
                ),
                default_properties AS(
                    SELECT DISTINCT ON (property.company_id, property.name)
                           'res.partner' AS model,
                           company.partner_id AS id,
                           CASE
                               WHEN property.name = 'property_account_receivable_id' THEN 'asset_receivable'
                               ELSE 'liability_payable'
                           END AS account_type,
                           SPLIT_PART(property.value_reference, ',', 2)::integer AS account_id
                      FROM ir_property property
                      JOIN res_company company ON property.company_id = company.id
                     WHERE property.name IN ('property_account_receivable_id', 'property_account_payable_id')
                       AND property.company_id = ANY(%(company_ids)s)
                       AND property.res_id IS NULL
                  ORDER BY property.company_id, property.name, account_id
                ),
                fallback AS (
                    SELECT DISTINCT ON (account.company_id, account.account_type)
                           'res.company' AS model,
                           account.company_id AS id,
                           account.account_type AS account_type,
                           account.id AS account_id
                      FROM account_account account
                     WHERE account.company_id = ANY(%(company_ids)s)
                       AND account.account_type IN ('asset_receivable', 'liability_payable')
                       AND account.deprecated = 'f'
                )
                SELECT * FROM previous
                UNION ALL
                SELECT * FROM default_properties
                UNION ALL
                SELECT * FROM properties
                UNION ALL
                SELECT * FROM fallback
            """, {
                'company_ids': moves.company_id.ids,
                'move_ids': moves.ids,
                'partners': [f'res.partner,{pid}' for pid in moves.commercial_partner_id.ids],
                'current_ids': term_lines.ids
            })
            accounts = {
                (model, id, account_type): account_id
                for model, id, account_type, account_id in self.env.cr.fetchall()
            }
            for line in term_lines:
                account_type = 'asset_receivable' if line.move_id.is_sale_document(include_receipts=True) else 'liability_payable'
                move = line.move_id
                account_id = (
                    accounts.get(('account.move', move.id, None))
                    or accounts.get(('res.partner', move.commercial_partner_id.id, account_type))
                    or accounts.get(('res.partner', move.company_id.partner_id.id, account_type))
                    or accounts.get(('res.company', move.company_id.id, account_type))
                )
                if line.move_id.fiscal_position_id:
                    account_id = self.move_id.fiscal_position_id.map_account(self.env['account.account'].browse(account_id))
                line.account_id = account_id

        product_lines = self.filtered(lambda line: line.display_type == 'product' and line.move_id.is_invoice(True))
        for line in product_lines:
            if line.product_id:
                fiscal_position = line.move_id.fiscal_position_id
                accounts = line.with_company(line.company_id).product_id\
                    .product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
                if line.move_id.is_sale_document(include_receipts=True):
                    line.account_id = accounts['income'] or line.account_id
                elif line.move_id.is_purchase_document(include_receipts=True):
                    line.account_id = accounts['expense'] or line.account_id
            elif line.partner_id:
                if line.acs_is_rg_line:
                    line.account_id = line.account_id.id
                else:
                    line.account_id = self.env['account.account']._get_most_frequent_account_for_partner(
                        company_id=line.company_id.id,
                        partner_id=line.partner_id.id,
                        move_type=line.move_id.move_type,
                    )
        for line in self:
            if not line.account_id and line.display_type not in ('line_section', 'line_note'):
                previous_two_accounts = line.move_id.line_ids.filtered(
                    lambda l: l.account_id and l.display_type == line.display_type and not line.acs_is_rg_line
                )[-2:].account_id
                if len(previous_two_accounts) == 1 and len(line.move_id.line_ids) > 2 and not line.acs_is_rg_line:
                    line.account_id = previous_two_accounts
                else:
                    if not line.acs_is_rg_line:
                        line.account_id = line.move_id.journal_id.default_account_id
