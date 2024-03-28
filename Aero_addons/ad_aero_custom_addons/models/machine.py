from odoo import api, fields, models, _, SUPERUSER_ID
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

class OrdreFabrication(models.Model):
    _inherit = 'mrp.workorder'

    def _get_default_norme_interne(self):
        if self.operation_id:
            return self.operation_id.norme_interne.id
        else:
            return False

    norme_interne = fields.Many2one(
        'norme',
        string="N. Interne",
        domain=[('type_norme', '=', 'interne'), ('state', 'in', ['conforme', 'derogation'])],
        default=_get_default_norme_interne
    )

    indice_ni = fields.Char(string="Indice NI", related="norme_interne.indice")
    # date_derogation_ni = fields.Datetime(string="Date DG NI",
    #                                      related="operation_id.norme_interne.date_fin_derogation")
    # date_archivage_ni = fields.Datetime(string="Date AC NI", related="norme_interne.date_archived")


    def _get_default_norme_externe(self):
        if self.operation_id:
            return self.operation_id.norme_externe.id
        else:
            return False

    norme_externe = fields.Many2one(
        'norme',
        string="N. Externe",
        domain=[('type_norme', '=', 'externe'), ('state', 'in', ['conforme', 'derogation'])],
        default=_get_default_norme_externe
    )

    indice_ne = fields.Char(string="Indice NE", related="norme_externe.indice")
    # date_derogation_ne = fields.Datetime(string="Date DG NE",
    #                                      related="norme_externe.date_fin_derogation")
    # date_archivage_ne = fields.Datetime(string="Date AC NE", related="norme_externe.date_archived")

