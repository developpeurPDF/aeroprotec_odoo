from odoo import models, fields

class CauseNonConformite(models.Model):
    _name = 'cause.non.conformite'
    _description = 'Cause de non conformité'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Cause de la non-conformité", tracking=True)


