# -*- coding: utf-8 -*-

from odoo import models, fields, api

class matiereParameterValue(models.Model):
    _name = 'matiere.parameter.value'
    _description = 'Matière'

    name = fields.Char("Matière", readonly=False, required=False)
    name_abreviation = fields.Char("Abréviation matière", readonly=False, required=False)
    active = fields.Boolean("Active", default=True, required=True)
    # rank = fields.Integer("Ordre", readonly=False, store=True)
    # parameter_code = fields.Char("Code paramètre", related="parameter_id.code", readonly=True, store=True)
    parameter_name = fields.Char("Nom Famille Matière", related="parameter_id.name", readonly=True, store=True)
    parameter_id = fields.Many2one('matiere.parameter', 'Famille Matière', index=True, ondelete='cascade', readonly=True)
    ref_ids = fields.One2many("matiere.parameter.ref", "parameter_id", "Nature de la matière")

    #parent_id = fields.Many2one('matiere.parameter.value', 'Parent', index=True, required=False)

class matiereParameterref(models.Model):
    _name = 'matiere.parameter.ref'
    _description = 'Nature de la matière'

    name = fields.Char("Nature de la matière", readonly=False, required=False)
    name_resistance = fields.Char("Résistance", readonly=False, required=False)
    active = fields.Boolean("Active", default=True, required=True)
    # rank = fields.Integer("Ordre", readonly=False, store=True)
    # parameter_code = fields.Char("Code paramètre", related="parameter_id.code", readonly=True, store=True)
    parameter_name = fields.Char("Nom Matière", related="parameter_id.name", readonly=True, store=True)
    parameter_id = fields.Many2one('matiere.parameter.value', 'Matière', index=True, ondelete='cascade', readonly=True)
    # resistance_ids = fields.One2many("matiere.parameter.resistance", "parameter_id", "Résistance")

# class matiereParameteresistance(models.Model):
#     _name = 'matiere.parameter.resistance'
#     _description = 'Résistance'
#
#     name = fields.Char("Résistance", readonly=False, required=False)
#     # name_en = fields.Char("Nom en", readonly=False, required=False)
#     active = fields.Boolean("Active", default=True, required=True)
#     # rank = fields.Integer("Ordre", readonly=False, store=True)
#     # parameter_code = fields.Char("Code paramètre", related="parameter_id.code", readonly=True, store=True)
#     parameter_name = fields.Char("Nom Réf Matière", related="parameter_id.name", readonly=True, store=True)
#     parameter_id = fields.Many2one('matiere.parameter.ref', 'Réf Matière', readonly=True)
#     test_ids = fields.One2many("matiere.parameter.test", "parameter_id", "test")
#
# class matiereParametetest(models.Model):
#     _name = 'matiere.parameter.test'
#     _description = 'test'
#
#     name = fields.Char("test", readonly=False, required=False)
#     # name_en = fields.Char("Nom en", readonly=False, required=False)
#     active = fields.Boolean("Active", default=True, required=True)
#     # rank = fields.Integer("Ordre", readonly=False, store=True)
#     # parameter_code = fields.Char("Code paramètre", related="parameter_id.code", readonly=True, store=True)
#     parameter_name = fields.Char("Nom Résistance Matière", related="parameter_id.name", readonly=True, store=True)
#     parameter_id = fields.Many2one('matiere.parameter.resistance', 'Resistance Matière', readonly=True)
#     # ref_ids = fields.One2many("matiere.parameter.ref", "parameter_id", "Réf matière")
    