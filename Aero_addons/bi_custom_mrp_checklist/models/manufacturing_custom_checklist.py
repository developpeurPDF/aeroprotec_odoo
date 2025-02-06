# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class ManufacturingChecklist(models.Model):
    _name = "manufacturing.checklist"
    _description = "Manufacturing Custom checklist"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")


class ManufacturingChecklistLine(models.Model):
    _name = "manufacturing.checklist.line"
    _description = "MRP Custom checklist Line"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Name ")
    checklist_id = fields.Many2one('manufacturing.checklist', string="Name")
    mrp_id = fields.Many2one("mrp.production", string="mrp id")
    description = fields.Char(string="Description")
    date = fields.Date(default=fields.Date.today)
    state = fields.Selection([
        ('new', 'New'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel')], string='State',
        copy=False, default="new")

    @api.onchange('checklist_id')
    def _onchange_checklist_id(self):
        for checklist in self:
            description = ''
            if checklist.checklist_id:
                description = checklist.checklist_id.description
            checklist.update({
                'description': description
            })

    def action_complete(self):
        for rec in self:
            rec.state = 'complete'
            checklist_len = len(rec.mrp_id.checklist_line_ids)
            completed_progress = len(rec.mrp_id.checklist_line_ids.filtered(lambda x: x.state == 'complete'))
            rec.mrp_id.write({
                'checklist_progress': (completed_progress * 100) / (checklist_len or 1)
            })

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            checklist_len = len(rec.mrp_id.checklist_line_ids)
            completed_progress = len(rec.mrp_id.checklist_line_ids.filtered(lambda x: x.state == 'complete'))
            rec.mrp_id.write({
                'checklist_progress': (completed_progress * 100) / (checklist_len or 1)
            })


class ManufacturingChecklistTemplate(models.Model):
    _name = "manufacturing.checklist.template"
    _description = "Manufacturing Custom Checklist Template"
    _rec_name = "template_name"

    sequence = fields.Integer(string="Sequence")
    template_name = fields.Char(string="Name")
    checklist_ids = fields.Many2many('manufacturing.checklist', string="Checklist Template")


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    checklist_progress = fields.Integer(string='Checklist Progress', store=True, default=0)
    checklist_template = fields.Many2many('manufacturing.checklist.template', string='MRP Checklist template')
    checklist_line_ids = fields.One2many('manufacturing.checklist.line', 'mrp_id', string='Checklist')

    @api.onchange('checklist_template')
    def onchange_checklist_template(self):

        if self.checklist_template:
            custom_checklist = []
            for template in self.checklist_template:
                for checklist in template.checklist_ids:
                    custom_checklist.append((0, 0, {
                        'checklist_id': checklist._origin.id,
                        'description': checklist.description,
                        'mrp_id': self.id,
                    }))
                    self.update({'checklist_line_ids': False})
            self.update({"checklist_line_ids": custom_checklist})
        else:
            self.update({'checklist_line_ids': False})
