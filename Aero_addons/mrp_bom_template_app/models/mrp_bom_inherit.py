# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Mrpbom(models.Model):
    _inherit = 'mrp.bom'

    mrp_bom_temp_id = fields.Many2one('mrp.bom.template',domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        check_company=True, string = "Bill Of Material Template")

    @api.onchange('mrp_bom_temp_id')
    def _onchange_bom_temp_id(self):
        if not self.product_tmpl_id and self.mrp_bom_temp_id:
            self.product_tmpl_id = self.mrp_bom_temp_id.product_tmpl_id
        self.product_qty = self.mrp_bom_temp_id.product_qty or 1.0
        self.product_uom_id = self.mrp_bom_temp_id and self.mrp_bom_temp_id.product_uom_id.id or self.product_id.uom_id.id
        self.code = self.mrp_bom_temp_id.code or False
        self.type = self.mrp_bom_temp_id.type
        self.bom_line_ids = [(5, 0, 0)]
        self.ready_to_produce = self.mrp_bom_temp_id.ready_to_produce
        self.consumption = self.mrp_bom_temp_id.consumption

        bom_lines = []
        open_lines = []
        product_lines=[]
        for line in self.mrp_bom_temp_id.bom_temp_line_ids:
            bom_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'product_tmpl_id': line.product_tmpl_id.id,
                'company_id': line.company_id.id,
                'product_uom_category_id': line.product_uom_category_id.id,
                'parent_product_tmpl_id': line.parent_product_tmpl_id.id,
            }))


        for line in self.mrp_bom_temp_id.operation_ids:
            open_lines.append((0, 0, {
                'name': line.name,
                'workcenter_id': line.workcenter_id.id,
                'sequence': line.sequence,
                'bom_temp_id': line.bom_temp_id.id,
                'company_id': line.company_id.id
            }))

        for line in self.mrp_bom_temp_id.byproduct_ids:
            product_lines.append((0, 0, {
                'company_id': line.company_id.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'allowed_operation_ids': [(6, 0, line.allowed_operation_ids.ids)],
                'product_uom_id': line.product_uom_id.id,
                'operation_id': line.operation_id.id
            }))
 
        self.bom_line_ids = bom_lines
        self.operation_ids = open_lines
        self.byproduct_ids = product_lines

        