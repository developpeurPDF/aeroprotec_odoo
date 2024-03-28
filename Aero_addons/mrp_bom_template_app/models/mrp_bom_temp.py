# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class MrpBomTemplate(models.Model):
    _name = 'mrp.bom.template'
    _rec_name = 'code'
    _order = 'sequence'


    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    bom_id = fields.Many2one(
        'mrp.bom', 'Modèle de nomenclatures',
        index=True, ondelete='cascade', required=False)

    name = fields.Char('Name', copy=False, readonly=True, default=lambda x: _('New'))
    active = fields.Boolean(
        'Active', default=True,
        help="If the active field is set to False, it will allow you to hide the bills of material without removing it.")
    code = fields.Char('Reference', required=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        check_company=True, index=True,
        domain="[('type', 'in', ['product', 'consu'])]", required=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        check_company=True, index=True,
        domain="['&', ('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', 'consu'])]",
        help="If a product variant is defined the BOM is available only for this product.")

    product_uom_category_id = fields.Many2one(related='product_tmpl_id.uom_id.category_id')
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of bills of material.")


    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=_get_default_product_uom_id, required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True,
        default=lambda self: self.env.company)

    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit'),('subcontract', 'Sous-traitance')], 'BoM Type',
        default='normal', required=True)

    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Unit of Measure', required=True)
    # route_id = fields.Many2one('bom.route.template', string="Modèle d'opération standard")

    bom_temp_line_ids = fields.One2many('mrp.bom.temp.line', 'bom_temp_id', 'BoM Lines', copy=True)
    # operation_ids = fields.One2many('mrp.routing.workcenter', 'bom_temp_id', 'Operations', copy=True)
    operation_ids = fields.Many2many('mrp.routing.workcenter', string="Operations", copy=True)
    byproduct_ids = fields.One2many('mrp.bom.temp.byproduct', 'bom_temp_id', 'By-products', copy=True)
    ready_to_produce = fields.Selection([
        ('all_available', ' When all components are available'),
        ('asap', 'When components for 1st operation are available')], string='Manufacturing Readiness',
        default='asap', help="Defines when a Manufacturing Order is considered as ready to be started", required=True)
    consumption = fields.Selection([
        ('flexible', 'Allowed'),
        ('warning', 'Allowed with warning'),
        ('strict', 'Blocked')],
        help="Defines if you can consume more or less components than the quantity defined on the BoM:\n"
             "  * Allowed: allowed for all manufacturing users.\n"
             "  * Allowed with warning: allowed for all manufacturing users with summary of consumption differences when closing the manufacturing order.\n"
             "  * Blocked: only a manager can close a manufacturing order when the BoM consumption is not respected.",
        default='warning',
        string='Flexible Consumption',
        required=True
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type', domain="[('code', '=', 'mrp_operation')]",
        check_company=True,
        help=u"When a procurement has a ‘produce’ route with a operation type set, it will try to create "
             "a Manufacturing Order for that product using a BoM of the same operation type. That allows "
             "to define stock rules which trigger different manufacturing orders with different BoMs.")

    produce_delay = fields.Float(
        'Durée du cycle', default=0.0,
        help="Average lead time in days to manufacture this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added. In case the product is subcontracted, this can be used to determine the date at which components should be sent to the subcontractor.")

    type_gamme = fields.Selection([
        ('production', 'GAMME DE PRODUCTION'),
        ('reprise', 'GAMME DE REPRISE'),('epouvettes', 'GAMME DES ARTICLES EPOUVETTES')], 'Type de gamme',
        )
    nb_traitement_surface = fields.Integer(string="Nombre de traitement de surface")

    @api.model 
    def create(self,vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.bom.template') or _('New')
        return super(MrpBomTemplate, self).create(vals)

    @api.onchange('bom_temp_line_ids', 'product_qty')
    def onchange_bom_structure(self):
        if self.type == 'phantom' and self._origin and self.env['stock.move'].search([('bom_line_id', 'in', self._origin.bom_temp_line_ids.ids)], limit=1):
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _(
                        'The product has already been used at least once, editing its structure may lead to undesirable behaviours. '
                        'You should rather archive the product and create a new one with a new bill of materials.'),
                }
            }


    @api.onchange('product_uom_id')
    def onchange_product_uom_id(self):
        res = {}
        if not self.product_uom_id or not self.product_tmpl_id:
            return
        if self.product_uom_id.category_id.id != self.product_tmpl_id.uom_id.category_id.id:
            self.product_uom_id = self.product_tmpl_id.uom_id.id
            res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
        return res

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_uom_id = self.product_tmpl_id.uom_id.id
            if self.product_id.product_tmpl_id != self.product_tmpl_id:
                self.product_id = False
            for line in self.bom_temp_line_ids:
                line.bom_product_template_attribute_value_ids = False






class MrpBomTempLine(models.Model):
    _name = 'mrp.bom.temp.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    product_id = fields.Many2one('product.product', 'Component', required=True, check_company=True, ondelete='cascade')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id',
                                      store=True)
    company_id = fields.Many2one(related='bom_temp_id.company_id', store=True, index=True, readonly=True)
    product_qty = fields.Float('Quantity', default=1.0, digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', default=_get_default_product_uom_id,
                                     required=True,
                                     help="Unit of Measure (Unit of Measure) is the unit of measurement for inventory control",
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    sequence = fields.Integer('Sequence', default=1, help="Gives the sequence order when displaying.")
    bom_temp_id = fields.Many2one('mrp.bom.template', 'Parent BoM', index=True, ondelete='cascade', required=True)
    parent_product_tmpl_id = fields.Many2one('product.template', 'Parent Product Template',
                                             related='bom_temp_id.product_tmpl_id')
    possible_bom_product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                                         compute='_compute_possible_bom_product_template_attribute_value_ids')
    bom_product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                                string="Apply on Variants", ondelete='restrict',
                                                                domain="[('id', 'in', possible_bom_product_template_attribute_value_ids)]",
                                                                help="BOM Product Variants needed to apply this line.")
    allowed_operation_ids = fields.Many2many('mrp.routing.workcenter', compute='_compute_allowed_operation_ids')
    operation_id = fields.Many2one('mrp.routing.workcenter', 'Consumed in Operation', check_company=True,
                                   domain="[('id', 'in', allowed_operation_ids)]",
                                   help="The operation where the components are consumed, or the finished products created.")
    attachments_count = fields.Integer('Attachments Count', compute='_compute_attachments_count')


    @api.depends('product_id')
    def _compute_attachments_count(self):
        for line in self:
            nbr_attach = self.env['mrp.document'].search_count([
                '|',
                '&', ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id),
                '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)])
            line.attachments_count = nbr_attach


    def action_see_attachments(self):
        domain = [
            '|',
            '&', ('res_model', '=', 'product.product'), ('res_id', '=', self.product_id.id),
            '&', ('res_model', '=', 'product.template'), ('res_id', '=', self.product_id.product_tmpl_id.id)]
        attachment_view = self.env.ref('mrp.view_document_file_kanban_mrp')
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'mrp.document',
            'type': 'ir.actions.act_window',
            'view_id': attachment_view.id,
            'views': [(attachment_view.id, 'kanban'), (False, 'form')],
            'view_mode': 'kanban,tree,form',
            'help': _('''<p class="o_view_nocontent_smiling_face">
                        Upload files to your product
                    </p><p>
                        Use this feature to store any files, like drawings or specifications.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d, 'default_company_id': %s}" % ('product.product', self.product_id.id, self.company_id.id)
        }


    @api.depends('bom_temp_id')
    def _compute_allowed_operation_ids(self):
        for bom_line in self:
            if not bom_line.bom_temp_id.operation_ids:
                bom_line.allowed_operation_ids = self.env['mrp.routing.workcenter']
            else:
                operation_domain = [
                    ('id', 'in', bom_line.bom_temp_id.operation_ids.ids),
                    '|',
                        ('company_id', '=', bom_line.company_id.id),
                        ('company_id', '=', False)
                ]
                bom_line.allowed_operation_ids = self.env['mrp.routing.workcenter'].search(operation_domain)


    @api.depends(
        'parent_product_tmpl_id.attribute_line_ids.value_ids',
        'parent_product_tmpl_id.attribute_line_ids.attribute_id.create_variant',
        'parent_product_tmpl_id.attribute_line_ids.product_template_value_ids.ptav_active',
    )
    def _compute_possible_bom_product_template_attribute_value_ids(self):
        for line in self:
            line.possible_bom_product_template_attribute_value_ids = line.parent_product_tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes().product_template_value_ids._only_active()



class MrpByTempProduct(models.Model):
    _name = 'mrp.bom.temp.byproduct'
    _rec_name = "product_id"
    _check_company_auto = True

    product_id = fields.Many2one('product.product', 'By-product', required=True, check_company=True)
    company_id = fields.Many2one(related='bom_temp_id.company_id', store=True, index=True, readonly=True)
    product_qty = fields.Float(
        'Quantity',
        default=1.0, digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    bom_temp_id = fields.Many2one('mrp.bom.template', 'BoM', ondelete='cascade')
    allowed_operation_ids = fields.Many2many('mrp.routing.workcenter', compute='_compute_allowed_operation_ids')
    operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Produced in Operation', check_company=True,
        domain="[('id', 'in', allowed_operation_ids)]")

    @api.depends('bom_temp_id')
    def _compute_allowed_operation_ids(self):
        for byproduct in self:
            if not byproduct.bom_temp_id.operation_ids:
                byproduct.allowed_operation_ids = self.env['mrp.routing.workcenter']
            else:
                operation_domain = [
                    ('id', 'in', byproduct.bom_temp_id.operation_ids.ids),
                    '|',
                        ('company_id', '=', byproduct.company_id.id),
                        ('company_id', '=', False)
                ]
                byproduct.allowed_operation_ids = self.env['mrp.routing.workcenter'].search(operation_domain)

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Changes UoM if product_id changes. """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('product_uom_id')
    def onchange_uom(self):
        res = {}
        if self.product_uom_id and self.product_id and self.product_uom_id.category_id != self.product_id.uom_id.category_id:
            res['warning'] = {
                'title': _('Warning'),
                'message': _('The unit of measure you choose is in a different category than the product unit of measure.')
            }
            self.product_uom_id = self.product_id.uom_id.id
        return res