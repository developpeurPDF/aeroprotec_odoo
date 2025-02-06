# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class quality_point(models.Model):
    _name = "quality.point"
    _description = "Quality Point"
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom")
    product_temp_id = fields.Many2one('product.template', string="Produit", required=True)
    product_id = fields.Many2one('product.product', string="Variante de produit", required=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation', required=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    test_type = fields.Selection([('pass_fail', 'Pass-Fail'), ('measure', 'Measure')], string="Type",
                                 default='pass_fail', required=True)
    norm = fields.Float('Norm')
    unit = fields.Char('unit')
    min_quality = fields.Float('Tolerance')
    max_quality = fields.Float('Max')
    user_id = fields.Many2one('res.users', string="Responsable")
    instruction = fields.Html(string="Instruction")
    message = fields.Html(string="Message If Fail")
    team_id = fields.Many2one('quality.team', string="Équipe")

    @api.onchange('product_temp_id')
    def onchange_product_temp_id(self):
        self.product_id = self.product_temp_id.product_variant_id

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('quality.point') or '/'
        vals['name'] = seq
        return super(quality_point, self).create(vals)


class quality_checks(models.Model):
    _name = "quality.checks"
    _description = "Quality Check"

    _inherit = ['mail.thread']

    name = fields.Char('Nom', default=lambda self: 'Check')
    
    product_id = fields.Many2one('product.product', string="Produit", required=True)
    lot_id = fields.Many2one('stock.lot', string="LOT")
    picking_id = fields.Many2one('stock.picking', string="Picking")
    quality_point_id = fields.Many2one('quality.point', string="Point de contrôle", required=True)
    state = fields.Selection([('do', 'To Do'), ('pass', "Pass"), ('fail', 'Fail')], default="do")
    measure = fields.Float(string="Mesure")
    note = fields.Html(string="Notes", related="quality_point_id.instruction")
    test_type = fields.Selection([('pass_fail', 'Pass-Fail'), ('measure', 'Measure')], string="Type",
                                 related="quality_point_id.test_type")
    unit = fields.Char(related="quality_point_id.unit")
    min_quality = fields.Float('Tolerance', related="quality_point_id.min_quality")
    max_quality = fields.Float('Max', related="quality_point_id.max_quality")
    team_id = fields.Many2one('quality.team', related="quality_point_id.team_id")
    date = fields.Date(string="Date")
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)

    def checks_next(self):
        res = self.env['stock.picking'].browse(self._context.get('active_id'))

        action = self.env.ref('warehouse_quality_control_app.action_check_wizard').read()[0]

        checks = self.env['quality.checks'].search([('picking_id', '=', res.id), ('state', '=', 'do')])

        for quality in checks:
            action['res_id'] = self.id

            return action

    def action_pass(self):
        self.write({'state': 'pass', 'date': fields.datetime.now().date()})
        self.checks_next()
        return

    def action_fail(self):
        self.write({'state': 'fail', 'date': fields.datetime.now().date()})
        self.checks_next()
        return

    def validate_check(self):

        if self.measure < self.min_quality or self.measure > self.max_quality:
            return {

                'type': 'ir.actions.act_window',
                'res_model': 'quality.checks',
                'view_mode': 'form',
                'res_id': self.id,
                'name': _('Quality Checks'),
                'view_id': self.env.ref('warehouse_quality_control_app.view_check_quality_fail').id,
                'target': 'new',

                'context': self.env.context,
            }

        else:

            self.action_pass()

    def action_reset(self):

        action = self.env.ref('warehouse_quality_control_app.action_check_wizard').read()[0]
        action['res_id'] = self.id
        return action

    def action_confirm(self):
        self.action_fail()

        return
