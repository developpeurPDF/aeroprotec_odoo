from odoo import models

class OrdreTravailReport(models.AbstractModel):
    _name = 'report.ad_aero_report_p4_1.ordre_travail_report_template'
    _description = 'Rapport Ordre de Travail'

    def _get_report_values(self, docids, data=None):

        selected_docs = self.env['mrp.workorder'].browse(docids)
        return {
            'docs': selected_docs,
        }
