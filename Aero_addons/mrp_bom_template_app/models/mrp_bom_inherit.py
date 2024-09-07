# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Mrpbom(models.Model):
    _inherit = 'mrp.bom'


    mrp_bom_temp_id = fields.Many2one('mrp.bom.template', string="Modèle de nomenclature",  domain="[('famille_matiere','=',produit_famille_matiere),'|',('company_id','=',False),('company_id','=',company_id)]")
    produit_famille_matiere = fields.Many2one('matiere.parameter', string="Famille matière", related="product_tmpl_id.famille_matiere")
    # bom_tmpl_famille_matiere = fields.Many2one('matiere.parameter', string="Famille matière", related="mrp_bom_temp_id.famille_matiere")

    @api.onchange('mrp_bom_temp_id')
    def _onchange_bom_temp_id(self):
        if not self.product_tmpl_id and self.mrp_bom_temp_id:
            self.product_tmpl_id = self.mrp_bom_temp_id.product_tmpl_id
        self.product_qty = self.mrp_bom_temp_id.product_qty or 1.0
        # self.product_uom_id = self.mrp_bom_temp_id and self.mrp_bom_temp_id.product_uom_id.id or self.product_id.uom_id.id
        self.code = self.mrp_bom_temp_id.code or False

        self.bom_line_ids = [(5, 0, 0)]
        if self.mrp_bom_temp_id:
            self.ready_to_produce = self.mrp_bom_temp_id.ready_to_produce
            self.consumption = self.mrp_bom_temp_id.consumption
            self.type = self.mrp_bom_temp_id.type
            self.type_gamme = self.mrp_bom_temp_id.type_gamme
            self.nb_traitement_surface = self.mrp_bom_temp_id.nb_traitement_surface

        bom_lines = []
        open_lines = []
        product_lines = []

        self.operation_ids.unlink()


        for line in self.mrp_bom_temp_id.bom_temp_line_ids:
            bom_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'product_tmpl_id': line.product_tmpl_id.id,
                'company_id': line.company_id.id,
                'product_uom_category_id': line.product_uom_category_id.id,
                'parent_product_tmpl_id': line.parent_product_tmpl_id.id,
            }))

        for line in self.mrp_bom_temp_id.operation_ids:

            vals =  {
                'name': line.name,
                'active': True,
                'workcenter_id': line.workcenter_id.id,
                'sequence': line.sequence,
                # 'bom_temp_id': line.bom_temp_id.id,
                'company_id': line.company_id.id,
                'code_operation': line.code_operation,
                'nature_operation': line.nature_operation.id,
                'abreviation_operation': line.abreviation_operation,
                'norme_interne': line.norme_interne.id,
                'norme_externe': line.norme_externe.id,
                'time_cycle_manual': line.time_cycle,
                'bom_id': self.id or self._origin.id,
                # 'phase': [(6, 0, [phase.id for phase in line.phase.id])] if line.phase.id else False
            }
            # Récupération des sous-opérations
            phases = []
            for phase_id in line.phase.ids:
                phase = self.env['phase.operation'].browse(phase_id)
                #print("yesss")
                phase_vals = {
                    'ordre': phase.ordre,
                    'name': phase.name,
                    'code': phase.code,
                    'note': phase.note,
                    # 'operations': operation.id,
                }
                phases.append((0, 0, phase_vals))
                #print("phases", phases)
            vals['phase'] = phases

            open_lines.append(tuple(vals.items()))
            

        for line in self.mrp_bom_temp_id.byproduct_ids:
            product_lines.append((0, 0, {
                'company_id': line.company_id.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'allowed_operation_ids': [(6, 0, line.allowed_operation_ids.ids)],
                'product_uom_id': line.product_uom_id.id,
                'operation_id': line.operation_id.id
            }))


        self.bom_line_ids = bom_lines
        self.operation_ids = self.env['mrp.routing.workcenter'].create(open_lines)
        self.byproduct_ids = product_lines









    # @api.onchange('mrp_bom_temp_id')
    # def _onchange_bom_temp_id(self):
    #     # Vous pouvez garder votre fonction existante ici
    #     if not self.product_tmpl_id and self.mrp_bom_temp_id:
    #         self.product_tmpl_id = self.mrp_bom_temp_id.product_tmpl_id
    #     self.product_qty = self.mrp_bom_temp_id.product_qty or 1.0
    #     self.product_uom_id = self.mrp_bom_temp_id and self.mrp_bom_temp_id.product_uom_id.id or self.product_id.uom_id.id
    #     self.code = self.mrp_bom_temp_id.code or False
    #     self.type = self.mrp_bom_temp_id.type
    #     self.bom_line_ids = [(5, 0, 0)]
    #     self.ready_to_produce = self.mrp_bom_temp_id.ready_to_produce
    #     self.consumption = self.mrp_bom_temp_id.consumption
    #
    #     bom_lines = []
    #     open_lines = []
    #     product_lines = []
    #     for line in self.mrp_bom_temp_id.bom_temp_line_ids:
    #         bom_lines.append((0, 0, {
    #             'product_id': line.product_id.id,
    #             'product_qty': line.product_qty,
    #             'product_uom_id': line.product_uom_id.id,
    #             'product_tmpl_id': line.product_tmpl_id.id,
    #             'company_id': line.company_id.id,
    #             'product_uom_category_id': line.product_uom_category_id.id,
    #             'parent_product_tmpl_id': line.parent_product_tmpl_id.id,
    #         }))
    #
    #     new_operations = []
    #
    #     # Ajoutez les nouvelles opérations à la liste temporaire
    #     for line in self.mrp_bom_temp_id.operation_ids:
    #         vals = {
    #             'name': line.name,
    #             'workcenter_id': line.workcenter_id.id,
    #             'sequence': line.sequence,
    #             'bom_temp_id': line.bom_temp_id.id,
    #             'company_id': line.company_id.id,
    #             'code_operation': line.code_operation,
    #             'nature_operation': line.nature_operation.id,
    #             'abreviation_operation': line.abreviation_operation,
    #             'norme_interne': line.norme_interne.id,
    #             'norme_externe': line.norme_externe.id,
    #             'ref_prog_automate': line.ref_prog_automate,
    #             'time_mode': line.time_mode,
    #             'time_cycle_manual': line.time_cycle_manual,
    #             'worksheet_type': line.worksheet_type,
    #             'note': line.note,
    #             'worksheet': line.worksheet,
    #             'worksheet_google_slide': line.worksheet_google_slide,
    #             'bom_id': self.id or self._origin.id,
    #         }
    #         new_operation = self.env['mrp.routing.workcenter'].create(vals)
    #         new_operations.append(new_operation)
    #
    #     # Ajoutez les nouvelles opérations à self.operation_ids
    #     self.operation_ids = [(4, op.id) for op in new_operations]
    #
    #     for line in self.mrp_bom_temp_id.byproduct_ids:
    #         product_lines.append((0, 0, {
    #             'company_id': line.company_id.id,
    #             'product_id': line.product_id.id,
    #             'product_qty': line.product_qty,
    #             'allowed_operation_ids': [(6, 0, line.allowed_operation_ids.ids)],
    #             'product_uom_id': line.product_uom_id.id,
    #             'operation_id': line.operation_id.id
    #         }))
    #
    #     self.bom_line_ids = bom_lines
    #     # Plutôt que de remplacer, étendre la liste d'opérations
    #     if open_lines:
    #         self.operation_ids += open_lines
    #     self.byproduct_ids = product_lines