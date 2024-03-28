from odoo import api, fields, models

# class MrpBom(models.Model):
#     _inherit='mrp.bom'
#
#     route_id = fields.Many2one('bom.route.template',string='Route')
#
#     @api.onchange('route_id')
#     def onchange_route_id(self):
#         if self.route_id:
#             if self.route_id.operation_ids:
#                 # Clear existing operations before adding new ones
#                 # self.operation_ids.unlink()
#                 operations = []
#                 for x in self.route_id.operation_ids:
#                     vals = {
#                         'name': x.name,
#                         'active': True,
#                         'workcenter_id': x.workcenter_id.id,
#                         'code_operation': x.code_operation,
#                         'nature_operation': x.nature_operation.id,  # Changed to store nature_operation ID
#                         'abreviation_operation': x.abreviation_operation,
#                         'type_operation': x.type_operation,
#                         'norme_interne': x.norme_interne.id,
#                         'norme_externe': x.norme_externe.id,
#                         'ref_prog_automate': x.ref_prog_automate,
#                         'time_mode': x.time_mode,
#                         'time_cycle_manual': x.time_cycle_manual,
#                         'worksheet_type': x.worksheet_type,
#                         'note': x.note,
#                         'worksheet': x.worksheet,
#                         'worksheet_google_slide': x.worksheet_google_slide,
#                         'bom_id': self.id or self._origin.id,
#                     }
#                     operation = self.env['mrp.routing.workcenter'].create(vals)
#                     # Append phase IDs to the operation
#                     operation.phase = [(6, 0, x.phase.ids)]
#                     operations.append(operation)
#
#                 self.code = self.route_id.name
#             else:
#                 self.operation_ids.unlink()
#                 self.code = self.route_id.name
#         else:
#             self.operation_ids.unlink()

#        metode 2




class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    route_id = fields.Many2one('bom.route.template', string="Modèle d'opérations")

    @api.onchange('route_id')
    def onchange_route_id(self):
        if self.route_id:
            operations = []
            for route_operation in self.route_id.operation_ids:
                # Vérifiez si une opération similaire existe déjà
                existing_operation = self.operation_ids.filtered(
                    lambda op: op.name == route_operation.name and op.workcenter_id == route_operation.workcenter_id
                )
                if existing_operation:
                    # Si l'opération existe déjà, mettez à jour ses valeurs
                    existing_operation.write({
                        'code_operation': route_operation.code_operation,
                        'nature_operation': route_operation.nature_operation.id,
                        'abreviation_operation': route_operation.abreviation_operation,
                        'type_operation': route_operation.type_operation,
                        'norme_interne': route_operation.norme_interne.id,
                        'norme_externe': route_operation.norme_externe.id,
                        'ref_prog_automate': route_operation.ref_prog_automate,
                        'time_mode': route_operation.time_mode,
                        'time_cycle_manual': route_operation.time_cycle_manual,
                        'worksheet_type': route_operation.worksheet_type,
                        'note': route_operation.note,
                        'worksheet': route_operation.worksheet,
                        'worksheet_google_slide': route_operation.worksheet_google_slide,
                    })
                else:
                    # Sinon, créez une nouvelle opération
                    vals = {
                        'name': route_operation.name,
                        'workcenter_id': route_operation.workcenter_id.id,
                        'code_operation': route_operation.code_operation,
                        'nature_operation': route_operation.nature_operation.id,
                        'abreviation_operation': route_operation.abreviation_operation,
                        'type_operation': route_operation.type_operation,
                        'norme_interne': route_operation.norme_interne.id,
                        'norme_externe': route_operation.norme_externe.id,
                        'ref_prog_automate': route_operation.ref_prog_automate,
                        'time_mode': route_operation.time_mode,
                        'time_cycle_manual': route_operation.time_cycle_manual,
                        'worksheet_type': route_operation.worksheet_type,
                        'note': route_operation.note,
                        'worksheet': route_operation.worksheet,
                        'worksheet_google_slide': route_operation.worksheet_google_slide,
                        'bom_id': self.id or self._origin.id,
                    }
                    operation = self.env['mrp.routing.workcenter'].create(vals)
                    # Append phase IDs to the operation
                    operation.phase = [(6, 0, route_operation.phase.ids)]
                    operations.append(operation)

            # Ajoutez les nouvelles opérations à operation_ids sans effacer les opérations existantes
            self.operation_ids = [(4, operation.id) for operation in operations] + [(4, op.id) for op in
                                                                                    self.operation_ids]

    # @api.onchange('route_id')
    # def onchange_route_id(self):
    #     if self.route_id:
    #         # if self.route_id.route_lines:
    #         operations = []
    #         for x in self.route_id.operation_ids:
    #             # self.write({'operation_ids': [(5, 0)]})
    #             # Récupération des sous-opérations
    #             # phases = []
    #             # for phase_id in x.phase.ids:
    #             #     phase = self.env['phase.operation'].browse(phase_id)
    #             #     print("yesss")
    #             #     phase_vals = {
    #             #         'ordre': phase.ordre,
    #             #         'name': phase.name,
    #             #         'code': phase.code,
    #             #         'note': phase.note,
    #             #         # 'operations': operation.id,
    #             #     }
    #             #     phases.append((0, 0, phase_vals))
    #             #     print("phases", phases)
    #             # vals['phase'] = phases
    #
    #             vals = {
    #                 'name': x.name,
    #                 'workcenter_id': x.workcenter_id.id,
    #                 'code_operation': x.code_operation,
    #                 'nature_operation': x.nature_operation.id,
    #                 'abreviation_operation': x.abreviation_operation,
    #                 # 'phase': phases,
    #                 'type_operation': x.type_operation,
    #                 'norme_interne': x.norme_interne.id,
    #                 'norme_externe': x.norme_externe.id,
    #                 'ref_prog_automate': x.ref_prog_automate,
    #                 'time_mode': x.time_mode,
    #                 'time_cycle_manual': x.time_cycle_manual,
    #                 'worksheet_type': x.worksheet_type,
    #                 'note': x.note,
    #                 'worksheet': x.worksheet,
    #                 'worksheet_google_slide': x.worksheet_google_slide,
    #                 'bom_id': self.id or self._origin.id,
    #             }
    #             operation = self.env['mrp.routing.workcenter'].create(vals)
    #             # Append phase IDs to the operation
    #             operation.phase = [(6, 0, x.phase.ids)]
    #
    #             operations.append(vals)
    #
    #         # self.operation_ids = [(5, 0, 0)]  # Supprimer les opérations existantes
    #         self.operation_ids = [(0, 0, operation) for operation in operations]
    #     #     else:
    #     #         self.operation_ids = [(5, 0, 0)]  # Supprimer les opérations existantes
    #     # else:
    #     #     self.operation_ids = [(5, 0, 0)]  # Supprimer les opérations existantes
    #
    #     self.code = self.route_id.name


