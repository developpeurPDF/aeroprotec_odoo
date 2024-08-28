# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command

class AccountTax(models.Model):
    _name = 'modes.reglement'

    name = fields.Char(string="Type de réglement")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)