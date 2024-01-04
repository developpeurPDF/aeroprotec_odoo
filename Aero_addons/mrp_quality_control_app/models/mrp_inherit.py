# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    quality_checks = fields.Boolean(string="Quality Checks", compute="_compute_quality_check")
    quality_point = fields.Boolean(string="Quality Point", copy=False)

    def open_quality_alert(self):
        action = self.env.ref('warehouse_quality_control_app.quality_alert_action_id').read()[0]
        action['domain'] = [('mrp_id', '=', self.id)]
        return action

    def create_quality_alert(self):
        view_id = self.env.ref('warehouse_quality_control_app.view_quality_alert_form').id
        return {
            'name': 'Quality Checks',
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
