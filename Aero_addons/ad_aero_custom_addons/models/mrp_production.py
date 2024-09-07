from odoo import api, fields, models, _
from math import pi

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_ids = fields.Many2one('sale.order', string="Bons de commande", compute='_compute_sale_order_ids')

    @api.depends('procurement_group_id')
    def _compute_sale_order_ids(self):
        for production in self:
            sale_orders = self.env['sale.order'].search(
                [('name', '=', production.origin)])
            production.sale_order_ids = sale_orders

    donneur_order = fields.Many2one('donneur.order', string="Donneur d'ordre", tracking=True)
    nom_donneur_order = fields.Char(string="Nom du Donneur d'ordre", related='donneur_order.name.name', readonly=True)
    codes = fields.Many2one('donneur.ordre.code', string="Code traitement" , domain="[('name_donneur_order', '=', nom_donneur_order)]", tracking=True)
    # code_traitement = fields.Char(string="Code traitement", related="donneur_order.codes")

    @api.depends('product_id')
    def _compute_bom_id(self):
        super(MrpProduction, self)._compute_bom_id()

        # Ajoutez votre logique personnalisée ici pour filtrer les BOM avec le state 'active'
        for production in self:
            if production.bom_id and production.bom_id.state != 'active':
                production.bom_id = False

    def action_confirm(self):
        self.split_production_order()
        res = super(MrpProduction, self).action_confirm()
        return res

    def split_production_order(self):
        for order in self:
            # Calculer le nombre de lots nécessaires en fonction de la capacité minimale des postes de travail
            capacity_list = [workcenter.default_capacity for workcenter in order.workorder_ids.mapped('workcenter_id')]
            min_capacity = min(capacity_list)
            num_lots = -(-order.product_qty // min_capacity)  # Division arrondie à l'entier supérieur

            # Variable temporaire pour suivre la quantité totale déjà planifiée
            total_qty_planned = 0

            # Créer les nouveaux ordres de fabrication avec les quantités appropriées
            for i in range(int(num_lots) - 1):
                new_order_qty = min_capacity if i < num_lots - 1 else order.product_qty % min_capacity or min_capacity
                total_qty_planned += new_order_qty
                new_order_vals = {
                    'product_id': order.product_id.id,
                    'product_uom_id': order.product_uom_id.id,
                    'product_qty': new_order_qty,
                    'origin': order.name,
                    'state': 'draft',  # Vous pouvez changer cet état selon vos besoins
                }

                # Créer un nouveau nom pour l'ordre de fabrication
                new_order_vals['name'] = order.name + ' - ' + chr(65 + i)

                new_order = self.create(new_order_vals)
            order.product_qty -= total_qty_planned
