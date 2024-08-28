# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MatiereParameterValue(models.Model):
    _name = 'matiere.parameter.value'
    _rec_names_search = ['name', 'name_abreviation']
    _description = 'Matière'

    name = fields.Char("Matière", readonly=False, required=False)
    name_abreviation = fields.Char("Abréviation matière", readonly=False, required=False)
    active = fields.Boolean("Active", default=True, required=True)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    parameter_name = fields.Char("Nom Famille Matière", related="parameter_id.name", readonly=True, store=True)
    parameter_id = fields.Many2one('matiere.parameter', 'Famille Matière', index=True, ondelete='cascade', readonly=True)
    ref_ids = fields.One2many("matiere.parameter.ref", "parameter_id", "Nature de la matière")

    # @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} : {record.name_abreviation}"
            result.append((record.id, name))
        return result


class matiereParameterref(models.Model):
    _name = 'matiere.parameter.ref'
    _description = 'Nature de la matière'

    name = fields.Char("Nature de la matière", readonly=False, required=False)
    name_resistance = fields.Char("Résistance", readonly=False, required=False)
    abreviation = fields.Char("Abréviation", readonly=False, required=False)
    active = fields.Boolean("Active", default=True, required=True)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    parameter_name = fields.Char("Nom Matière", related="parameter_id.name", readonly=True, store=True)
    parameter_id = fields.Many2one('matiere.parameter.value', 'Matière', index=True, ondelete='cascade', readonly=True)
