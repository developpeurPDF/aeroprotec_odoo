# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Activite(models.Model):
    _name = 'activite'
    _description = 'Activité'

    name = fields.Char(string="Libellé d'activité")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True)

class MotifDeBlocageDeLancement(models.Model):
    _name = 'motif.blocage.lancement'
    _description = 'Motif de blocage de lancement'

    name = fields.Char(string="Libellé de motif de blocage de lancement")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True)

class ClasseFonctionnelle(models.Model):
    _name = 'classe.fonctionnelle'
    _description = 'Classe Fonctionnelle'

    name = fields.Char(string="Libellé de classe fonctionnelle")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True)

class ProgrammeAeronautique(models.Model):
    _name = 'programme.aeonautique'
    _description = 'Programme aéronautique '

    name = fields.Char(string="Libellé de programme aéronautique ")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True)