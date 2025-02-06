# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"
    _description = 'Material Purchase Requisition Lines'

    
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Demandes', 
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
    )
#     layout_category_id = fields.Many2one(
#         'sale.layout_category',
#         string='Section',
#     )
    description = fields.Char(
        string='Description',
        required=True,
    )
    qty = fields.Float(
        string='Quantité',
        default=1,
        required=True,
    )
    uom = fields.Many2one(
        'uom.uom',#product.uom in odoo11
        string='Unité de mesure',
        required=True,
    )
    partner_id = fields.Many2many(
        'res.partner',
        string='Fournisseurs',
    )
    requisition_type = fields.Selection(
        selection=[
                    ('internal','Sélection interne'),
                    ('purchase','Bon de commande'),
        ],
        string='Action de demande',
        default='purchase',
        required=True,
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            # rec.description = rec.product_id.name
            rec.description = rec.product_id.display_name
            rec.uom = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
