from odoo import models, fields, api, _
import base64
from io import BytesIO
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    message = fields.Text(string="Message", readonly=True)

    def action_check_and_print(self):
        for record in self:
            if any(check.state == "do" for workorder in record.workorder_ids for check in workorder.check_ids):
                record.message = "Une ou plusieurs étapes des ordres de travail sont encore en état 'ToDo'. Vous ne pouvez pas imprimer le rapport."
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Attention!',
                    'view_mode': 'form',
                    'res_model': 'mrp.production',
                    'target': 'new',
                    'views': [(self.env.ref('ad_aero_report_p4_1.view_mrp_production_popup_form').id, 'form')],
                }
        return self.env.ref("ad_aero_report_p4_1.control_libertoire_final_report_action").report_action(record)
    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}


    #show_button = fields.Char(string="show", related="operations.check_ids.state")

    #barcode = fields.Char(string="Code-barres", readonly=True, copy=False)
    #barcode_image = fields.Binary(string="Code-barres (Image)", readonly=True)
    
    @api.model
    def generate_barcode(self, production_id):
        """Génère un code-barres unique basé sur l'ID de l'ordre de fabrication"""
        return f"MRP-{production_id:08d}"

    def _generate_barcode_image(self, barcode_value):
        """Génère une image de code-barres en base64"""
        barcode = code128.Code128(barcode_value, barWidth=0.5 * mm, barHeight=15 * mm)
        drawing = Drawing(200, 50)
        drawing.add(barcode)

        buffer = BytesIO()
        drawing.save(formats=['png'], outFile=buffer)
        buffer.seek(0)

        return base64.b64encode(buffer.read())

    #@api.model
    #def create(self, vals):
        #"""Surcharge de la méthode create pour générer automatiquement le code-barres et #son image"""
        #production = super().create(vals)
        #barcode_value = self.generate_barcode(production.id)
        #production.barcode = barcode_value
        #production.barcode_image = self._generate_barcode_image(barcode_value)
        #return production
