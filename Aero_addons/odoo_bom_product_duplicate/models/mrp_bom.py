# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    previous_product_tmpl_id = fields.Many2one(
        'product.template',
        string="Previous Product Template",
        copy=False,
        readonly=True,
    )
    previous_product_id = fields.Many2one(
        'product.product',
        string="Previous Product",
        copy=False,
        readonly=True,
    )
