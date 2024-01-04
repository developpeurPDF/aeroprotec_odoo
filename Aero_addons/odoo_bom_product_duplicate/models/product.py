# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

#    @api.multi #odoo13
    def copy(self, default=None):
        product = super(
            ProductTemplate, self
        ).copy(default=default)

        bom_ids = self.env['mrp.bom'].sudo().search(
            [('product_tmpl_id', '=', self.id)]
        )
        if bom_ids:
            for bom in bom_ids:
                bom.copy(default={
                    'product_tmpl_id': product.id,
                    'previous_product_tmpl_id': self.id
                })
        return product


class ProductProduct(models.Model):
    _inherit = 'product.product'

#    @api.multi #odoo13
    def copy(self, default=None):
        product = super(
            ProductProduct, self
        ).copy(default=default)

        bom = self.env['mrp.bom'].sudo().search(
            [('product_id', '=', self.id),
             ('product_tmpl_id', '=', self.product_tmpl_id.id)]
        )

        if bom:
            bom.copy(default={
                'product_id': product.id,
                'product_tmpl_id': product.product_tmpl_id.id,
                'previous_product_tmpl_id': self.product_tmpl_id.id,
                'previous_product_id': self.id,
            })

        return product

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
