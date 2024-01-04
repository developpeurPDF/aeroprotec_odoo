# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    custom_price_subtotal = fields.Float(
        'Total BOM Cost',
        compute='_compute_price_subtotal',
        store=True,
    )
    
    @api.depends('bom_line_ids.custom_price_unit', 
        'bom_line_ids.product_qty',
        'bom_line_ids.custom_price_subtotal',
    )
    def _compute_price_subtotal(self):
        for rec in self:
            rec.custom_price_subtotal = 0.0
            for line in rec.bom_line_ids:
                rec.custom_price_subtotal += line.custom_price_subtotal


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    custom_price_unit = fields.Float(
        'Cost',
        # digits=dp.get_precision('Product Price'),
        digits='Product Price',
    )
    custom_price_subtotal = fields.Float(
        'Total Cost',
        compute='_compute_price_sbutotal',
        store=True,
    )

    def init(self):
        self._cr.execute("SELECT id FROM mrp_bom_line WHERE custom_price_unit IS NULL")
        res = self._cr.dictfetchall()
        line_ids = [l['id'] for l in res] 
        for line in self.sudo().browse(line_ids):
            line.write({'custom_price_unit' : line.product_id.standard_price})

    @api.depends('custom_price_unit',
                 'product_qty', 'product_uom_id')
    def _compute_price_sbutotal(self):
        for rec in self:
            if rec.product_id.uom_id and rec.product_uom_id: 
                if rec.product_id.uom_id != rec.product_uom_id:
                    custom_price_unit = rec.product_id.uom_id._compute_price(rec.custom_price_unit, rec.product_uom_id)
                    rec.custom_price_subtotal = rec.product_qty * custom_price_unit
                else:
                    rec.custom_price_subtotal = rec.product_qty * rec.custom_price_unit
            else:
                rec.custom_price_subtotal = rec.product_qty * rec.custom_price_unit
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.custom_price_unit = self.product_id.standard_price
        return super(MrpBomLine, self).onchange_product_id()
