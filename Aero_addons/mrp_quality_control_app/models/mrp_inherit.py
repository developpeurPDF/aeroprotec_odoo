# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    quality_checks = fields.Boolean(string="Contrôles de qualité", compute="_compute_quality_check")
    quality_point = fields.Boolean(string="Point de qualité", copy=False)
  

    def open_quality_alert(self):
        action = self.env.ref('warehouse_quality_control_app.quality_alert_action_id').read()[0]
        action['domain'] = [('mrp_id', '=', self.id)]
        return action

    def create_quality_alert(self):
        view_id = self.env.ref('warehouse_quality_control_app.view_quality_alert_form').id
        return {
            'name': 'Contrôles de qualité',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {'mrp_res': self.id},
            'res_model': 'quality.alert',
            'views': [(view_id, 'form')],

        }

    def button_mark_done(self):
        res = super(mrp_production, self).button_mark_done()
        checks = self.env['quality.checks'].search([('mrp_id', '=', self.id), ('state', '=', 'do')])
        if checks:
            raise UserError(_(' You still need to do the quality checks!'))
        return res

    def _compute_quality_check(self):
        for line in self:
            quality_checks = self.env['quality.checks'].search([('mrp_id', '=', line.id), ('state', '=', 'do')])
            if quality_checks:
                line.quality_checks = True
            else:
                line.quality_checks = False
        return

    def action_check_wizard_picking(self):
        action = self.env.ref('warehouse_quality_control_app.action_check_wizard').read()[0]
        checks = self.env['quality.checks'].search([('mrp_id', '=', self.id), ('state', '=', 'do')], )
        for quality in checks:
            action['res_id'] = quality.id
            return action

    def action_open_checkes(self):
        action = self.env.ref('warehouse_quality_control_app.qualitychecks_action_id').read()[0]
        action['domain'] = [('mrp_id', '=', self.id)]
        return action

    def _generate_finished_moves(self):

        res = super(mrp_production, self)._generate_finished_moves()
        quality_checks = self.env['quality.point'].search(
            [('picking_type_id', '=', self.picking_type_id.id), ('product_id', '=', self.product_id.id),
             ('company_id', '=', self.company_id.id)], order="id desc", limit=1)

        if quality_checks:
            self.quality_point = True

            self.env['quality.checks'].create({'product_id': self.product_id.id,
                                               'mrp_id': self.id,
                                               'quality_point_id': quality_checks.id,
                                               'state': 'do',
                                               })

        return res




class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_pending(self):

        if self.env.context.get('popup_validated', False):
            # Continuez l'action principale
            return super(MrpWorkorder, self).button_pending()
        """Supering the pause button to set timesheet in progress state and trigger popup."""
        res = super(MrpWorkorder, self).button_pending()

        # Logique existante (elle n'a pas besoin d'être modifiée si elle fonctionne déjà)
        project = self.env['project.project'].search(
            [('name', '=', ("MO: {}".format(self.production_id.name)))])
        task_id = project.task_ids.search([('name', '=', (
            "{} in {} for {} on {}".format(self.name, self.workcenter_id.name,
                                           self.product_id.display_name,
                                           str(self.date_planned_start))))])
        task_id.write({'planned_hours': self.duration_expected})

        timesheet = task_id.mapped('timesheet_ids')
        hours = int(self.duration)
        minutes = int((self.duration - hours) * 60)
        total_hours = (minutes / 60) + hours
        for rec in timesheet:
            rec.write({'unit_amount': total_hours})

        # Affichage du popup
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.workorder.popup',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_workorder_id': self.id,
            },
        }



    total_fabricated_qty = fields.Integer(
        string="Quantité Totale Fabriquée",
        compute='_compute_total_fabricated_qty',
        store=True
    )

    @api.depends('time_ids.quantite_fabrique')
    def _compute_total_fabricated_qty(self):
        for workorder in self:
            workorder.total_fabricated_qty = sum(line.quantite_fabrique for line in workorder.time_ids)

    def check_production_qty_limit(self):
        """
        Vérifie si la somme des quantités fabriquées dépasse la quantité prévue dans production_id.
        """
        for workorder in self:
            total_qty = sum(line.quantite_fabrique for line in workorder.time_ids)
            if total_qty > workorder.production_id.product_qty:
                raise UserError((
                                    "La somme des quantités fabriquées (%s) dépasse la quantité prévue (%s). "
                                    "Veuillez ajuster les quantités."
                                ) % (total_qty, workorder.production_id.product_qty))

    @api.model
    def create(self, vals):
        workorder = super(MrpWorkorder, self).create(vals)
        workorder.check_production_qty_limit()
        return workorder

    def write(self, vals):
        res = super(MrpWorkorder, self).write(vals)
        self.check_production_qty_limit()
        return res



    code_operation = fields.Char(string="Code opération", compute="_compute_code_operation")
    type_operation = fields.Selection([
            ('prestation', 'Prestation'),
            ('traitement_surface', 'Traitement de surface'),
            ('peinture', 'Peinture'),
            ('cnd', 'CND'),
        ],string="Type opération", compute="_compute_code_operation")

    @api.depends('operation_id')
    def _compute_code_operation(self):
        for record in self:
            if record.operation_id:
                record.code_operation = record.operation_id.code_operation
                record.type_operation = record.operation_id.type_operation
                # print("record.code_operation",record.code_operation)
            else:
                record.code_operation = False
                record.type_operation = False
                # print("record.code_operationV", record.code_operation)


    quality_check_ids = fields.One2many('quality.checks', 'workorder_id', string="Quality Checks")

    is_quality_checks_created = fields.Boolean(
        string="Contrôles de qualité créés",
        default=False,
    )

    def button_start(self):
        res = super(MrpWorkorder, self).button_start()

        for workorder in self:
            # Récupérer les `quality.point` où le `code_operation` correspond
            points = self.env['quality.point'].search([
                ('operation_id.code_operation', '=', workorder.code_operation),
                ('donneur_order', '=', workorder.production_id.donneur_order.id),
                ('type_article', '=', workorder.production_id.product_id.product_tmpl_id.type_article),
                ('matiere', '=', workorder.production_id.product_id.product_tmpl_id.matiere.id),
                ('type_gamme', '=', workorder.production_id.bom_id.type_gamme),

            ])

            # Vérifier les conditions supplémentaires et créer les Quality Checks
            if workorder.name and workorder.production_id.bom_id.product_tmpl_id and points:
                for point in points:
                    quality_check_vals = {
                        'note': f'Contrôle pour {workorder.production_id.bom_id.product_tmpl_id.name}',
                        'product_id': workorder.production_id.product_id.id,
                        'quality_point_id': point.id,
                        'workorder_id': workorder.id,
                        'point_qualite': point.point_qualite,
                    }
                    # Créer les Quality Checks pour cet ordre de travail
                    self.env['quality.checks'].create(quality_check_vals)

            # Ajouter les points qualité au champ Many2many dans l'ordre de travail
            if points:
                workorder.quality_point_ids = [(4, point.id) for point in points]

        return res

    quality_point_ids = fields.Many2many(
        'quality.point',
        'quality_point_workorder_rel',
        'workorder_id',
        'alert_id',
        string="Point de qualité"
    )

class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    quantite_fabrique = fields.Integer(string="Quantité Fabriquée")
    matricule = fields.Char(
        string="Matricule", 
        compute="_compute_matricule"
    )

    @api.depends('user_id')
    def _compute_matricule(self):
        for record in self:
            
            if record.user_id and record.user_id.employee_ids:
                record.matricule = record.user_id.employee_ids.matricule
            else:
                record.matricule = False