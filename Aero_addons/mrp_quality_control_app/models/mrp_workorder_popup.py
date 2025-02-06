from datetime import datetime
from odoo import fields, models


class MrpWorkOrderPopup(models.TransientModel):
    _name = 'mrp.workorder.popup'
    _description = 'Popup for Adding Time and Quantity'

    workorder_id = fields.Many2one('mrp.workorder', required=True)
    qty_done = fields.Float(string='Quantité effectuée', required=True)

    quality_check_ids = fields.One2many(
        related='workorder_id.quality_check_ids',
        string="Contrôles de qualité",
        readonly=False,
    )

    def action_add_time(self):
        """Add the entered quantity to the last line or create a new one."""
        # Récupérer la dernière ligne existante pour ce workorder_id
        last_record = self.env['mrp.workcenter.productivity'].search(
            [('workorder_id', '=', self.workorder_id.id)],
            order='id desc', limit=1
        )
        # print("last_record",last_record)

        if last_record:
            # Ajouter la quantité effectuée à la dernière ligne
            last_record.quantite_fabrique += self.qty_done
        else:
            # Créer une nouvelle entrée si aucune ligne n'existe
            self.env['mrp.workcenter.productivity'].create({
                'workorder_id': self.workorder_id.id,
                'quantite_fabrique': self.qty_done,
            })

        return {'type': 'ir.actions.act_window_close'}