# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class mrp_production_inherit(models.Model):
    _inherit = 'mrp.production'

    def _generate_workorders(self, exploded_boms):

        res = super(mrp_production_inherit, self)._generate_workorders(exploded_boms)

        for wo in res:
            quality_checks = self.env['quality.point'].search(
                [('picking_type_id', '=', self.picking_type_id.id), ('product_id', '=', self.product_id.id),
                 ('company_id', '=', self.company_id.id)], order="id desc", limit=1)

            if quality_checks:
                wo.quality_point = True
                self.env['quality.checks'].create({'product_id': self.product_id.id,
                                                   'mrp_id': self.id,
                                                   'workorder_id': wo.id,
                                                   'quality_point_id': quality_checks.id,
                                                   'state': 'do',

                                                   })

        return res


class mrp_production(models.Model):
    _inherit = 'mrp.workorder'

    quality_checks = fields.Boolean(string="Contrôles de qualité", compute="_compute_quality_check")
    quality_point = fields.Boolean(string="Point de qualité", copy=False)
    check_ids = fields.One2many('quality.checks', 'workorder_id', string="Contrôles de qualité")

    def open_quality_alert(self):

        action = self.env.ref('warehouse_quality_control_app.quality_alert_action_id').read()[0]
        action['domain'] = [('mrp_id', '=', self.production_id.id)]

        return action

    def create_quality_alert(self):

        view_id = self.env.ref('warehouse_quality_control_app.view_quality_alert_form').id

        return {
            'name': 'Contrôles de qualité',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'mrp_res': self.production_id.id},
            'res_model': 'quality.alert',
            'views': [(view_id, 'form')],

        }

    def record_production(self):
        res = super(mrp_production, self).record_production()

        checks = self.env['quality.checks'].search([('workorder_id', '=', self.id), ('state', '=', 'do')])

        # if checks :
        #     raise UserError(_(' You still need to do the quality checks!'))

        return res

    def _compute_quality_check(self):
        # print("advance mrp")
        for line in self:

            quality_checks = self.env['quality.checks'].search([('workorder_id', '=', line.id), ('state', '=', 'do')])

            if quality_checks:
                line.quality_checks = True

            else:

                line.quality_checks = False

        return

    def action_check_wizard_picking(self):
        action = self.env.ref('warehouse_quality_control_app.action_check_wizard').read()[0]

        quality_checks = self.env['quality.point'].search(
            [('picking_type_id', '=', self.production_id.picking_type_id.id),
             ('product_id', '=', self.production_id.product_id.id),
             ('company_id', '=', self.production_id.company_id.id)], order="id desc", limit=1)

        checks = self.env['quality.checks'].search([('workorder_id', '=', self.id), ('state', '=', 'do')], )

        print('\n\n1111111===lity_checks====>', quality_checks)
        if not checks:
            checks = self.env['quality.checks'].create({'product_id': self.production_id.product_id.id,
                                                        'mrp_id': self.production_id.id,
                                                        'workorder_id': self.id,
                                                        'quality_point_id': quality_checks.id,
                                                        'state': 'do',

                                                        })

        for quality in checks:

            if quality.product_id.tracking != 'none':
                lot_id = self.finished_lot_id.id

                quality.write({'lot_id': lot_id})

            action['res_id'] = quality.id

            return action

    def action_open_checkes(self):

        action = self.env.ref('warehouse_quality_control_app.qualitychecks_action_id').read()[0]
        action['domain'] = [('workorder_id', '=', self.id)]

        return action
