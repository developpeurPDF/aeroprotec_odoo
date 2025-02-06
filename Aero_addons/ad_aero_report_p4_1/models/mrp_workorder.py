from odoo import api, fields, models

class OrdreFabrication(models.Model):
    _inherit = 'mrp.workorder'

    #phase_id = fields.Many2many(
        #'phase.operation',
       # 'workorder_phase_rel',
       # 'workorder_id',
      #  'phase_id',
      #  string="Sous-Opérations"
   # )


    def _get_report_values(self, docids, data=None):

        docs = self.env['mrp.workorder'].browse(docids)
        return {
            'docs': docs,
        }

