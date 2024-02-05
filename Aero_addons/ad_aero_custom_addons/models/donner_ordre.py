from odoo import api, fields, models, _
from math import pi
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

class DonneurOrder(models.Model):
    _name = 'donneur.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.partner', string="Donneur d'ordre", required=True, tracking=True,)
    company_id = fields.Many2one('res.company', string="Société", tracking=True,)
    codes = fields.One2many('donneur.ordre.code', 'donneur_order', string="Codes", tracking=True)
    norme = fields.One2many('norme', 'donneur_order', string="Norme", tracking=True,)
    # codes = fields.One2many('donneur.ordre.code', 'donneur_order', string="Codes", tracking=True, tracking_force=True)


class CodeDonneurOrder(models.Model):
    _name = 'donneur.ordre.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Code",required=True, tracking=True,)
    abrege = fields.Char(string="Abréviation", tracking=True,)
    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True,)
    name_donneur_order = fields.Char(string="Nom de donneur d'ordre", related="donneur_order.name.name", readonly=True, tracking=True,)
    company_id = fields.Many2one('res.company', string="Société", tracking=True,)