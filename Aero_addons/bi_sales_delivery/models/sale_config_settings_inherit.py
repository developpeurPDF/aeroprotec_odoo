# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
	_inherit = 'res.company'


	allow_delivery_date = fields.Boolean(string="Autoriser la date de livraison dans la ligne de commande vente", default=False)


class ResConfigSettings(models.TransientModel): 
	_inherit = 'res.config.settings'

	allow_delivery_date = fields.Boolean(string="Autoriser la date de livraison dans la ligne de commande vente", related='company_id.allow_delivery_date',readonly=False,)
