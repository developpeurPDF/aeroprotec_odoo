from odoo import api, fields, models, _
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

class DonneurOrder(models.Model):
    _name = 'donneur.order'

    name = fields.Many2one('res.partner', string="Donneur d'ordre")
    company_id = fields.Many2one('res.company', string="Société")
    codes = fields.One2many('donneur.ordre.code', 'donneur_order', string="Codes")

class CodeDonneurOrder(models.Model):
    _name = 'donneur.ordre.code'

    name = fields.Char(string="Code")
    abrege = fields.Char(string="Abrégé")
    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre")
    name_donneur_order = fields.Char(string="Nom de donneur d'ordre", related="donneur_order.name.name", readonly=True, )
    company_id = fields.Many2one('res.company', string="Société")