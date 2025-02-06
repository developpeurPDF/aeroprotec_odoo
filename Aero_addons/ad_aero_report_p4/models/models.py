from odoo import api, fields, models, _
from math import pi

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

class OrdreFabrication(models.Model):
    _inherit = 'mrp.workorder'

    def _get_default_documents(self):
        if self.operation_id:
            return self.operation_id.worksheet_ids
        else:
            return False

    worksheet_ids = fields.Many2many(
        'mrp.routing.worksheets',
        string="Doucuments",
        default=_get_default_documents
    )
