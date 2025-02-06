from odoo import models, fields

class CauseNonDetection(models.Model):
    _name = 'cause.non.detection'
    _description = 'Causes de Non-Détection'

    name = fields.Char(string="Cause de la non détection", tracking=True)

