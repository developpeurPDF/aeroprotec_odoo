# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class AccessManager(models.Model):
    _name = "ad.access.manager"
    _description = "Access Management"

    name = fields.Char("Name")
    responsible_user_ids = fields.Many2many("res.users",string="Utilisateurs")
    company_id = fields.Many2one("res.company",string="Société")
    created_by = fields.Many2one("res.users",string="Créé par")
    active_rule = fields.Boolean("Active",default="True")

    # pages
    ad_hide_menu_ids = fields.Many2many(comodel_name="ir.ui.menu",string="Masquer menu")
    ad_access_model_line = fields.One2many("ad.access.model",'access_manager_id',string="Accès Modèles")
    ad_field_access_line = fields.One2many("ad.field.access",'access_manager_id',string="Accès champs")
    ad_navbar_button_line = fields.One2many('ad.navbar.buttons.access','access_manager_id','Accès Navbar Button')
    ad_hide_chatter_line = fields.One2many("ad.hide.chatter",'access_manager_id',string="Masquer Chatter")

    def write(self,vals):
        self.env['ir.ui.menu'].sudo().clear_caches()
        # field_access = self.env['ad.field.access'].sudo().fields_view_get()
        # print("\n\n\n\n>>>>>> field_access >>>", field_access)
        res = super(AccessManager,self).write(vals)
        return res
    
    def unlink(self):
        self.ad_navbar_button_line.unlink()
        return super(AccessManager, self).unlink()
