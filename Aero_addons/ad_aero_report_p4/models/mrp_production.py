from odoo import models, fields, api
import base64
from io import BytesIO
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm

class ProductionMRP(models.Model):
    _inherit = "mrp.production"

    def action_check(self):
        for record in self:
            
            if any(check.state == "do" for workorder in record.workorder_ids for check in workorder.check_ids):
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        #'title': _('Attention!'),
                        'message': "Une ou plusieurs étapes des ordres de travail sont encore en état 'ToDo'. Vous ne pouvez pas imprimer le rapport.",
                        'type': 'warning', 
                        'sticky': False, 
                    },
                }
        
            return self.env.ref("ad_aero_report_p4.ordre_de_fabrication_report").report_action(record)