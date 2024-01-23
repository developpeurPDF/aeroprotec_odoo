# -*- coding: utf-8 -*-

from odoo import models, fields, api

class matiereParameter(models.Model):
    _name = 'matiere.parameter'
    _description = 'Famille matière'


    name = fields.Char("Famille matière", readonly=False, required=False)

    active = fields.Boolean("Active", default=True, readonly=True, required=True)
    values_ids = fields.One2many("matiere.parameter.value", "parameter_id", "Matière")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True)



