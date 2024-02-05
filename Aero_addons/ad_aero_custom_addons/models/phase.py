from odoo import api, fields, models, _
from math import pi

class PhaseOperation(models.Model):
    _name = 'phase.operation'

    ordre = fields.Integer(string="Ordre")
    name = fields.Char(string="Sous opérations",required=True,)
    code = fields.Char(string="Code")

    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    operations = fields.Many2one('mrp.routing.workcenter', string="Opérations")
    note = fields.Html(string="Note")

class NatureOperation(models.Model):
    _name = 'nature.operation'

    name = fields.Char(string="Nature d'opération", required=True, )


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    nature_operation = fields.Many2one('nature.operation', string="Nature d'opérations", tracking=True)
    phase = fields.One2many('phase.operation','operations', string="Sous opérations", tracking=True)
    # norme_ = fields.Many2one('norme', string="Norme Interne")
    norme_interne = fields.Many2one('norme', string="Norme Interne", domain=[('type_norme','=', 'interne'), ('state','in',['conforme', 'derogation'])], tracking=True)
    norme_externe = fields.Many2one('norme', string="Norme Externe", domain=[('type_norme','=','externe'), ('state','in',['conforme', 'derogation'])], tracking=True)
    # code = fields.Char(string="Code")
    ref_prog_automate = fields.Char(string="Référence programme automate")
    competance = fields.Text(string="Compétences")
    abreviation_operation = fields.Char(string="Abréviation de l’opération", tracking=True)
    code_operation = fields.Char(string="Code de l’opération", tracking=True)
    type_operation = fields.Selection([
            ('prestation', 'Prestation'),
            ('traitement_surface', 'Traitement de surface'),
            ('peinture', 'Peinture'),
            ('cnd', 'CND'),
        ],
        string="Type opération",
        default='prestation', tracking=True)

    operation_ts = fields.Selection(selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ], string="Opérations de TS", compute= "_compute_operation_ts")

    def _compute_operation_ts(self):
        for rec in self:
            if rec.type_operation in ["traitement_surface", "peinture"]:
                rec.operation_ts = "Oui"
            else:
                rec.operation_ts = "Non"
