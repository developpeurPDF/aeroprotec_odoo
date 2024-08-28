
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.move'

    is_conforme = fields.Selection([('conforme', 'Conforme'), ('non_conforme', 'Non Conforme')], string="Conformité", readonly=True)
    quality_control_id = fields.Many2one('quality.control', string="Contrôle Qualité", readonly=True)

    quality_control_done = fields.Boolean(string="Quality Control Done", default=False)

    def action_open_quality_control(self):
        """Open the quality control record linked to this stock move"""
        self.ensure_one()
        if self.quality_control_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contrôle Qualité',
                'view_mode': 'form',
                'res_model': 'quality.control',
                'res_id': self.quality_control_id.id,
                'target': 'new',
            }
