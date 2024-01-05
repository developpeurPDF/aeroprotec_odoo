# -*- coding: utf-8 -*-

from odoo import models, fields, api

class matiereParameter(models.Model):
    _name = 'matiere.parameter'
    _description = 'Famille matière'

    # code = fields.Char("Code", readonly=False, required=False)
    name = fields.Char("Famille matière", readonly=False, required=False)
    #is_master = fields.Boolean("Master paramètre", readonly=True,  required=True)
    active = fields.Boolean("Active", default=True, readonly=True, required=True)
    values_ids = fields.One2many("matiere.parameter.value", "parameter_id", "Matière")
    # ref_ids = fields.One2many("matiere.parameter.ref", "parameter_id", "Réf matière")
    # resistance_ids = fields.One2many("matiere.parameter.resistance", "parameter_id", "Résistance")


