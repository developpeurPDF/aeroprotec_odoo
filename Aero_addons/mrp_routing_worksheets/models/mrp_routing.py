from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    worksheet_ids = fields.One2many('mrp.routing.worksheets', 'operation_id', string="Fiches de travail sur l'addition")

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    worksheet_ids = fields.One2many(related='operation_id.worksheet_ids', readonly=True)
    worksheet_ids_count = fields.Integer(compute='_compute_worksheet_ids')

    @api.depends('worksheet_ids')
    def _compute_worksheet_ids(self):
        for record in self:
            record.worksheet_ids_count = len(record.worksheet_ids)

class MrpRoutingWorkcenter(models.Model):
    _name = 'mrp.routing.worksheets'

    operation_id = fields.Many2one('mrp.routing.workcenter', 'Opération')
    name = fields.Char('Nom', required=True)
    type = fields.Selection([
        ('INSTRUCTION', 'INSTRUCTION'), ('SPECIFICATION_TECHNIQUE', 'SPECIFICATION TECHNIQUE'),
        ('GAMME_CATS', 'GAMME CATS'), ('NORME_RESSUAGE', 'NORME RESSUAGE')
        , ('NORME_MARQUAGE', ' NORME MARQUAGE'), ('NORME_PEINTURE', 'NORME PEINTURE')
        , ('NORME_TS', 'NORME TS')],
        string="Type",)
    code = fields.Char('Code', required=True)
    validation = fields.Selection([
        ('oui', 'Validé'), ('non', 'Non Validé'),],
        string="Validation", )
    worksheet_type = fields.Selection([
        ('pdf', 'PDF'), ('google_slide', 'Google Slide'), ('text', 'Text')],
        string="Feuille de travail", default="text"
    )
    note = fields.Html('Description')
    worksheet = fields.Binary('PDF')
    worksheet_google_slide = fields.Char('Google Slide', help="Collez l'URL de votre diapositive Google. Assurez-vous que l'accès au document est public.")
