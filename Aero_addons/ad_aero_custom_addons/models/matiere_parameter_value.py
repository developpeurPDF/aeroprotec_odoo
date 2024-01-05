# -*- coding: utf-8 -*-

from odoo import models, fields, api

class matiereParameterValue(models.Model):
    _name = 'matiere.parameter.value'
    _description = 'Matière'

    name = fields.Char("Matière", readonly=False, required=False)
    name_abreviation = fields.Char("Abréviation matière", readonly=False, required=False)
    active = fields.Boolean("Active", default=True, required=True)
   
    parameter_name = fields.Char("Nom Famille Matière", related="parameter_id.name", readonly=True, store=True)
    parameter_id = fields.Many2one('matiere.parameter', 'Famille Matière', index=True, ondelete='cascade', readonly=True)
    ref_ids = fields.One2many("matiere.parameter.ref", "parameter_id", "Nature de la matière")

    

class matiereParameterref(models.Model):
    _name = 'matiere.parameter.ref'
    _description = 'Nature de la matière'

    name = fields.Char("Nature de la matière", readonly=False, required=False)
    name_resistance = fields.Char("Résistance", readonly=False, required=False)
    active = fields.Boolean("Active", default=True, required=True)

    parameter_name = fields.Char("Nom Matière", related="parameter_id.name", readonly=True, store=True)
    parameter_id = fields.Many2one('matiere.parameter.value', 'Matière', index=True, ondelete='cascade', readonly=True)
