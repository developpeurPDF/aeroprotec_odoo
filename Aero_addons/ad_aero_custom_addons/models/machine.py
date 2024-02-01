from odoo import api, fields, models, _
from math import pi

class Machine(models.Model):
    _inherit = 'maintenance.equipment'


    etat = fields.Selection([
            ('operationnelle', 'Opérationnelle'),
            ('inoperante', 'Inopérante')
        ],
        string="Etat de la machine",
        default='operationnelle', tracking=True,)
    capacite_horaire = fields.Float(string="Capacité horaire", tracking=True)
    duree_prg = fields.Float(string="Durée du programme", tracking=True)
    capacite_piece = fields.Integer(string="Capacité en pièce", tracking=True)
    nb_lot = fields.Integer(string="Nombre de lot", tracking=True)
    poste_travail_id = fields.Many2one('mrp.workcenter', string="Poste de travail", tracking=True)

class PosteTravail(models.Model):
    _inherit = 'mrp.workcenter'

    # machine = fields.One2many('maintenance.equipment','poste_travail', string="Machine")
    machines_ids = fields.One2many('maintenance.equipment', 'poste_travail_id', string="Machines")

