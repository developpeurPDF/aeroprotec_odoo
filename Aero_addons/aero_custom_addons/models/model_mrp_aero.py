# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Activite(models.Model):
    _name = 'activite'
    _description = 'Activité'

    name = fields.Char(string="Libellé d'activité")

class MotifDeBlocageDeLancement(models.Model):
    _name = 'motif.blocage.lancement'
    _description = 'Motif de blocage de lancement'

    name = fields.Char(string="Libellé de motif de blocage de lancement")

class ClasseFonctionnelle(models.Model):
    _name = 'classe.fonctionnelle'
    _description = 'Classe Fonctionnelle'

    name = fields.Char(string="Libellé de classe fonctionnelle")

class ProgrammeAeronautique(models.Model):
    _name = 'programme.aeonautique'
    _description = 'Programme aéronautique '

    name = fields.Char(string="Libellé de programme aéronautique ")