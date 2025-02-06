from odoo import models, fields

class CauseOccurrence(models.Model):
    _name = 'cause.occurrence'
    _description = 'Causes Occurrence'

    name = fields.Char(string="Cause d'occurrence et non détection", tracking=True)
