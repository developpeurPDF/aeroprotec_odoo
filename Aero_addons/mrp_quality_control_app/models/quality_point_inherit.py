# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _


class Quality_point(models.Model):
    _inherit = 'quality.point'

    operation_id = fields.Many2one('mrp.routing.workcenter', string="Workorder Operation Center")
    code = fields.Selection(
        [('mrp_operation', 'Manufacturing Operation'), ('incoming', 'Vendors'), ('outgoing', 'Customers'),
         ('internal', 'Internal')], related="picking_type_id.code", string="Code")
    test_type = fields.Selection(
        [('pass_fail', 'Pass-Fail'), ('measure', 'Measure'), ('picture', 'Take a Picture'), ('text', 'Text')],
        string="Type", default='pass_fail')


class Quality_check(models.Model):
    _inherit = 'quality.checks'

    mrp_id = fields.Many2one('mrp.production', string="Production Name")
    workorder_id = fields.Many2one('mrp.workorder', string="Work-order")
    picture = fields.Binary(string="Photo")
    test_type = fields.Selection(
        [('pass_fail', 'Pass-Fail'), ('measure', 'Measure'), ('picture', 'Take a Picture'), ('text', 'Text')],
        string="Type", default='pass_fail', related="quality_point_id.test_type")

    def validate_picture(self):
        self.write({'state': 'pass', 'date': fields.datetime.now().date()})
        return

    def validate_text(self):
        self.write({'state': 'pass', 'date': fields.datetime.now().date()})
        return


class Quality_alert(models.Model):
    _inherit = 'quality.alert'

    mrp_id = fields.Many2one('mrp.production', string="Production Name")

    @api.model
    def default_get(self, default_fields):
        res = super(Quality_alert, self).default_get(default_fields)
        if self._context.get('mrp_res'):
            mrp_res = self.env['mrp.production'].browse(int(self._context.get('mrp_res')))
            res['product_id'] = mrp_res.product_id.id
            res['product_temp_id'] = mrp_res.bom_id.product_tmpl_id.id
            res['date_assigned'] = fields.datetime.now()
        res = self._convert_to_write(res)
        return res

    @api.model
    def create(self, vals):

        seq = self.env['ir.sequence'].next_by_code('quality.alert') or '/'
        vals['name'] = seq
        if self._context.get('mrp_res'):
            vals['mrp_id'] = int(self._context.get('mrp_res'))

            # mrp_res = self.env['mrp.production'].browse(int(self._context.get('mrp_res')))

        return super(Quality_alert, self).create(vals)
