from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    matricule = fields.Char(string="Matricule")
    signature = fields.Image(string="Signature", max_width=1024, max_height=1024)
