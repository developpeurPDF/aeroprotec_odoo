from odoo import api, fields, models, _
from math import pi

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_ids = fields.Many2one('sale.order', string="Bons de commande", compute='_compute_sale_order_ids')
    observation = fields.Html(string="Observation")
    type_of = fields.Selection([
        ('production', 'Production'),
        ('eprouvette', 'Eprouvette'),
        ('reprise_nc', 'Reprise NC')
    ], string="Type OF")
    reference_article = fields.Char(related='product_id.default_code', string="Réf d'article")
    designation_article = fields.Char(related='product_id.name', string="Désignation")
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Ligne CMD Clt",
        compute="_compute_sale_order_line_id",
        store=True,
        readonly=True,
    )
    priorite_globale = fields.Float(string="Priorité Glbe")

    type_ligne_commande = fields.Char(string="Type Ligne Commande")

    @api.depends('procurement_group_id')
    def _compute_sale_order_line_id(self):
        """Recalculate the associated sale order line."""
        for production in self:
            if production.procurement_group_id:
                sale_order_lines = self.env['sale.order.line'].search([
                    ('order_id.procurement_group_id', '=', production.procurement_group_id.id)
                ])
                production.sale_order_line_id = sale_order_lines[:1] if sale_order_lines else False

                #production._recalculate_type_ligne_commande()
            else:
                production.sale_order_line_id = False
                production.type_ligne_commande = False
                
    client = fields.Many2one(
        'res.partner',
        related='sale_order_line_id.order_partner_id',
        string="Client",
        readonly=True,
    )
    equipe_controle = fields.Many2one(
        'quality.team',
        string="Equipe de contrôle"
    )
    type_cmd = fields.Char(
        compute='_compute_type_cmd',
        string="Type Cmd",
        readonly=True,
    )
    @api.depends('type_ligne_commande')
    def _compute_type_cmd(self):
        type_ligne_dict = {
        'aog': 'AOG',
        'code_rouge': 'CODE ROUGE',
        'fil_rouge': 'FIL ROUGE',
        'horizon_flexible': 'Horizon flexible',
        'horizon_previsionnel': 'Horizon prévisionnel',
        'appel_de_livraison': 'Appel de livraison',
        'prestation': 'Prestation',
        'retour_client': 'Retour Client',
        'reparation': 'Reparation',
        'commande_ferme': 'COMMANDE FERME',
        'aog_reparation': 'AOG REPARATION',
        'autres': 'AUTRES',
        }
        for production in self:
            
            if production.type_ligne_commande:
                #production.type_cmd = production.type_ligne_commande
                production.type_cmd = type_ligne_dict.get(production.type_ligne_commande, production.type_ligne_commande)
       
            else:
                production.type_cmd = False

    n_of_interne = fields.Char(
        string="N° OF Clt",
        compute="_compute_n_of_interne",
        readonly=True,
    )

    @api.depends('sale_order_line_id')
    def _compute_n_of_interne(self):
        for production in self:
            
            if production.sale_order_line_id:
                production.n_of_interne = production.sale_order_line_id.n_of_interne.name
            else:
                production.n_of_interne = False

    ref_commande_interne = fields.Char(
        related='sale_order_line_id.order_id.name',
        string="CMD Int",
        readonly=True,
    )
    
    ref_commande_client = fields.Char(
        related='sale_order_line_id.order_id.client_order_ref',
        string="CMD Clt",
        readonly=True,
    )
    n_poste = fields.Char(
        string="N° Poste",
        compute="_compute_n_poste",
        readonly=True,
    )
    @api.depends('sale_order_line_id')
    def _compute_n_poste(self):
        
        for production in self:
            sale_order_line = production.sale_order_line_id
            if sale_order_line and hasattr(sale_order_line, 'n_poste_client'):
                production.n_poste = sale_order_line.n_poste_client
            else:
                production.n_poste = False

    
    gamme = fields.Char(
        string="Gamme",
        related='bom_id.code',
        readonly=True,
    )
    @api.depends('sale_order_line_id')
    def _compute_gamme(self):
       
        for production in self:
            sale_order_line = production.sale_order_line_id
            if sale_order_line and hasattr(sale_order_line, 'ref_gamme'):
                production.gamme = sale_order_line.ref_gamme
            else:
                production.gamme = False

    qty_commandee = fields.Float(
        string="Qté CMD",
        compute="_compute_qty_commandee",
        store=True,
        readonly=True,
    )
    qty_lancee = fields.Float(
        string="Qté Lancée",
        compute="_compute_qty_lancee",
        store=True,
        readonly=True,
    )
    date_recale = fields.Date(
        string="Date Recalé",
        compute="_compute_date_recale",
        store=True,
        readonly=True,
    )
    @api.depends('sale_order_line_id')
    def _compute_qty_commandee(self):
      
        for production in self:
            sale_order_line = production.sale_order_line_id
            if sale_order_line and hasattr(sale_order_line, 'qty_invoiced'):
                production.qty_commandee = sale_order_line.qty_invoiced
            else:
                production.qty_commandee = 0.0

    @api.depends('sale_order_line_id')
    def _compute_qty_lancee(self):
        
        for production in self:
            sale_order_line = production.sale_order_line_id
            if sale_order_line and hasattr(sale_order_line, 'qty_to_deliver'):
                production.qty_lancee = sale_order_line.qty_to_deliver
            else:
                production.qty_lancee = 0.0

    @api.depends('sale_order_line_id')
    def _compute_date_recale(self):
       
        for production in self:
            sale_order_line = production.sale_order_line_id
            if sale_order_line and hasattr(sale_order_line, 'date_recale'):
                production.date_recale = sale_order_line.date_recale
            else:
                production.date_recale = False

    

    @api.depends('sale_order_ids')
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
