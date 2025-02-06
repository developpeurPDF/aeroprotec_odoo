# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _, api

class AccessManager(models.Model):
    _name = "ad.access.model"
    _description = "Store All the Values that needs to be restricted model wise"

    model_id = fields.Many2one('ir.model',string="Modèle")
    view_ids = fields.Many2many('ad.view.list',string="Masquer Vues")
    # view_ids = fields.Many2many('ir.ui.view',string="Hide Views")
    access_manager_id = fields.Many2one("ad.access.manager",string="Gestionnaire d'accès")
    report_ids = fields.Many2many('ir.actions.report',domain="[('binding_model_id','=',model_id)]",string="Masquer rapports")
    # report_ids = fields.Many2many('ir.actions.report',string="Hide Reports")
    action_id = fields.Many2one(comodel_name="ir.actions.actions",domain="[('binding_model_id','=',model_id),('binding_type', '=', 'action')]",string="Masquer Actions")
    # action_id = fields.Many2one(comodel_name="ir.actions.actions",string="Hide Actions", domain="[('binding_model_id', '=', model_id)]")
    hide_create = fields.Boolean("Masquer bouton Créer")
    hide_edit = fields.Boolean("Masquer bouton Modifier")
    hide_duplicate = fields.Boolean("Masquer bouton Dupliquer")
    hide_delete = fields.Boolean("Masquer bouton Supprimer")
    hide_archieve = fields.Boolean("Masquer bouton Archive")
    hide_export = fields.Boolean("Masquer bouton Exporter")

    @api.model
    def check_crud_operation(self,kwargs):
        domain = [('access_manager_id.active_rule', '=', True),('access_manager_id.responsible_user_ids', 'in', [int(kwargs['user_id'])])]
        find_model_access = self.env['ad.access.model'].sudo().search(domain)        
        model_data = {}
        if find_model_access:   
            model_list = []
            for rec in find_model_access:
                if rec.model_id.sudo().model not in model_list:
                    model_list.append(rec.model_id.sudo().model)
                    records = find_model_access.filtered(lambda x :x.model_id == rec.model_id)
                    hide_create = False
                    hide_edit = False
                    hide_duplicate = False
                    hide_delete = False
                    hide_archieve = False
                    hide_export = False
                    for data in records:                        
                        if not hide_create and data.hide_create:                    
                            hide_create = True
                        if not hide_edit and data.hide_edit:                    
                            hide_edit = True
                        if not hide_duplicate and data.hide_duplicate:                    
                            hide_duplicate = True
                        if not hide_delete and data.hide_delete:                    
                            hide_delete = True
                        if not hide_archieve and data.hide_archieve:                    
                            hide_archieve = True
                        if not hide_export and data.hide_export:                    
                            hide_export = True                
                        model_data[data.model_id.sudo().model] = {
                            'hide_create' : not hide_create,
                            'hide_edit' : not hide_edit,
                            'hide_duplicate' : not hide_duplicate,
                            'hide_delete' : not hide_delete,
                            'hide_archieve' : not hide_archieve,
                            'hide_export' : not hide_export
                        }
        return model_data
