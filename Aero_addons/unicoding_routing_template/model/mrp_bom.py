from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit='mrp.bom'

    route_id = fields.Many2one('bom.route.template',string='Route')

    @api.onchange('route_id')
    def onchange_route_id(self):
        if self.route_id:
            if self.route_id.route_lines:
                self.write({
                    'operation_ids':[(5, 0)]
                })
                operations = []
                for x in self.route_id.route_lines:
                    vals={
                        'name':x.operation_name,
                        'workcenter_id':x.workcenter_id.id,
                        'sequence':x.sequence,
                        'time_mode':x.time_mode,
                        'time_mode_batch':x.time_mode_batch,
                        'time_cycle_manual':x.time_cycle_manual,
                        'worksheet_type':x.worksheet_type,
                        'note':x.note,
                        'worksheet':x.worksheet,
                        'worksheet_google_slide':x.worksheet_google_slide,
                        #'bom_id':self.id or self._origin.id,
                    }
                    operations.append(vals)
                    #work_center = self.env['mrp.routing.workcenter'].create(vals)
                   
                   
                self.code = self.route_id.name
                self.write({
                    'operation_ids': [(0, 0, operation) for operation in operations]
                })
            else:
                self.write({
                    'operation_ids': [(5, 0)]
                })
                self.code = self.route_id.name
                return
        else:
            return