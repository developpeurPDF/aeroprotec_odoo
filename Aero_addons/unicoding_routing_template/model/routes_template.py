from odoo import api, fields, models

class BOMRouteTemplate(models.Model):
    _name='bom.route.template'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,default=lambda self: self.env.company)
    route_lines = fields.One2many('bom.route.template.line','route_id', string='Route Lines')
    note = fields.Text(string='Note')

    # operation_ids = fields.One2many(
    #     'mrp.routing.workcenter', 'route_id', string='Produced in Operation', check_company=True)
    operation_ids = fields.Many2many(
        'mrp.routing.workcenter', string='Produced in Operation', check_company=True)

    # phase = fields.One2many('phase.operation','operations', string="Sous opérations", related="operation_ids.phase")

class BOMRouteTemplateLine(models.Model):
    _name='bom.route.template.line'

    route_id = fields.Many2one('bom.route.template', string='Route', required=True)

    operation_id = fields.One2many(
        'mrp.routing.workcenter', 'route_id',string='Produced in Operation', check_company=True)

    operation_name = fields.Char(string='Operation', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter',string='Work Center', required=True)
    sequence = fields.Integer(string='Sequence')
    time_mode = fields.Selection([
        ('auto', 'Compute based on tracked time'),
        ('manual', 'Set duration manually')], string='Duration Computation',
        default='manual')
    time_mode_batch = fields.Integer('Based on', default=10)
    time_cycle_manual = fields.Float(
        'Manual Duration', default=60,
        help="Time in minutes:"
             "- In manual mode, time used"
             "- In automatic mode, supposed first time when there aren't any work orders yet")
    worksheet_type = fields.Selection([
        ('pdf', 'PDF'), ('google_slide', 'Google Slide'), ('text', 'Text')],
        string="Work Sheet", default="text",
        help="Defines if you want to use a PDF or a Google Slide as work sheet."
    )
    note = fields.Text('Description', help="Text worksheet description")
    worksheet = fields.Binary('PDF')
    worksheet_google_slide = fields.Char('Google Slide',help="Paste the url of your Google Slide. Make sure the access to the document is public.")

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    route_id = fields.Many2one('bom.route.template', string='Route')

# class MrpBomTemplate(models.Model):
#     _inherit = 'mrp.bom.template'
#
#     route_id = fields.Many2one('bom.route.template', string="Modèle d'opération standard")
#
#     @api.onchange('route_id')
#     def onchange_route_id(self):
#         if self.route_id:
#             if self.route_id.operation_ids:
#                 self.write({
#                     'operation_ids': [(5, 0)]
#                 })
#                 operations = []
#                 for x in self.route_id.operation_ids:
#                     vals = {
#                         'name': x.name,
#                         'workcenter_id': x.workcenter_id.id,
#                         'sequence': x.sequence,
#                         'time_mode': x.time_mode,
#                         'time_mode_batch': x.time_mode_batch,
#                         'time_cycle_manual': x.time_cycle_manual,
#                         'worksheet_type': x.worksheet_type,
#                         'note': x.note,
#                         'worksheet': x.worksheet,
#                         'worksheet_google_slide': x.worksheet_google_slide,
#                         # 'bom_id':self.id or self._origin.id,
#                     }
#                     operations.append(vals)
#                     # work_center = self.env['mrp.routing.workcenter'].create(vals)
#
#                 # self.code = self.route_id.name
#                 self.write({
#                     'operation_ids': [(0, 0, operation) for operation in operations]
#                 })
#             else:
#                 self.write({
#                     'operation_ids': [(5, 0)]
#                 })
#                 self.code = self.route_id.name
#                 return
#         else:
#             return

    # @api.onchange('route_id')
    # def onchange_route_id(self):
    #     if self.route_id:
    #         operations = []
    #         for route_operation in self.route_id.operation_ids:
    #             # Vérifiez si une opération similaire existe déjà
    #             existing_operation = self.operation_ids.filtered(
    #                 lambda op: op.name == route_operation.name and op.workcenter_id == route_operation.workcenter_id
    #             )
    #             if existing_operation:
    #                 # Si l'opération existe déjà, mettez à jour ses valeurs
    #                 existing_operation.write({
    #                     'code_operation': route_operation.code_operation,
    #                     'nature_operation': route_operation.nature_operation.id,
    #                     'abreviation_operation': route_operation.abreviation_operation,
    #                     'type_operation': route_operation.type_operation,
    #                     'norme_interne': route_operation.norme_interne.id,
    #                     'norme_externe': route_operation.norme_externe.id,
    #                     'ref_prog_automate': route_operation.ref_prog_automate,
    #                     'time_mode': route_operation.time_mode,
    #                     'time_cycle_manual': route_operation.time_cycle_manual,
    #                     'worksheet_type': route_operation.worksheet_type,
    #                     'note': route_operation.note,
    #                     'worksheet': route_operation.worksheet,
    #                     'worksheet_google_slide': route_operation.worksheet_google_slide,
    #                 })
    #             else:
    #                 # Sinon, créez une nouvelle opération
    #                 vals = {
    #                     'name': route_operation.name,
    #                     'workcenter_id': route_operation.workcenter_id.id,
    #                     'company_id': self.company_id.id,
    #                     'code_operation': route_operation.code_operation,
    #                     'nature_operation': route_operation.nature_operation.id,
    #                     'abreviation_operation': route_operation.abreviation_operation,
    #                     'type_operation': route_operation.type_operation,
    #                     'norme_interne': route_operation.norme_interne.id,
    #                     'norme_externe': route_operation.norme_externe.id,
    #                     'ref_prog_automate': route_operation.ref_prog_automate,
    #                     'time_mode': route_operation.time_mode,
    #                     'time_cycle_manual': route_operation.time_cycle_manual,
    #                     'worksheet_type': route_operation.worksheet_type,
    #                     'note': route_operation.note,
    #                     'worksheet': route_operation.worksheet,
    #                     'worksheet_google_slide': route_operation.worksheet_google_slide,
    #                     # 'bom_id': self.id or self._origin.id,
    #                 }
    #                 operation = self.env['mrp.routing.workcenter'].create(vals)
    #                 # Append phase IDs to the operation
    #                 operation.phase = [(6, 0, route_operation.phase.ids)]
    #                 operations.append(operation)
    #
    #         # Ajoutez les nouvelles opérations à operation_ids sans effacer les opérations existantes
    #         self.operation_ids = [(4, operation.id) for operation in operations] + [(4, op.id) for op in
    #                                                                                 self.operation_ids]
