# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api

class SmartButtonList(models.Model):
    _name = "ad.hide.chatter"
    _description = "Smart Button List"

    name = fields.Char("Nom Navbar")
    model_ids = fields.Many2many('ir.model',string="Modèle")
    access_manager_id = fields.Many2one("ad.access.manager",string="Gestionnaire d'accès")

    @api.model
    def checkhide_chatter(self,kwargs):
        domain = [('access_manager_id.active_rule', '=', True),('access_manager_id.responsible_user_ids', 'in', [int(kwargs['user_id'])])]
        find_records = self.env['ad.hide.chatter'].sudo().search(domain)
        record_list = []
        if find_records:
            for records in find_records:
                for record in records.sudo().model_ids:
                    if record.model not in record_list:
                        record_list.append(record.model)
        return record_list