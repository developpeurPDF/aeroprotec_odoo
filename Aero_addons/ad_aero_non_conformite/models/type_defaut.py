from odoo import models, fields

class TypeDefaut(models.Model):
    _name = 'type.defaut'
    _description = 'Type de Défaut'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Type", tracking=True)


