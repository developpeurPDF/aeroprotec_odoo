from odoo import api, fields, models, _
from math import pi
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from datetime import datetime, timedelta

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    _order = 'priority desc, priorite_globale desc'


    sale_order_line_id = fields.Many2one('sale.order.line', string="Ligne de commande liée")

    type_ligne_commande = fields.Selection(related='sale_order_line_id.type_ligne', string="Type de la ligne",
                                           store=True)

    priority = fields.Selection(
        PROCUREMENT_PRIORITIES, string='Priority', default='0',
        help="Components will be reserved first for the MO with the highest priorities.")

    priorite_ligne_commande = fields.Integer(string="Priorité ligne de commande", compute="_compute_priorite_ligne_commande", store=True)

    priorite_date_livraison = fields.Integer(string="Priorité Date Livraison",
                                             compute="_compute_priorite_date_livraison", store=True)
    # priorite_capacite = fields.Integer(string="Priorité Capacité", compute="_compute_priorite_capacite", store=True)
    priorite_globale = fields.Float(string="Priorité Globale", compute="_compute_priorite_globale", store=True)

    @api.depends('type_ligne_commande')
    def _compute_priorite_ligne_commande(self):
        priority_mapping = {
            'Horizon_flexible': 0,
            'Horizon_previsionnel': 0,
            'Appel_de_livraison': 50,
            'Prestation': 0,
            'Retour_Client': 60,
            'Reparation': 50,
            'COMMANDE_FERME': 50,
            'aog': 80,
            'fil_rouge': 90,
            'AOG_REPARATION': 80
        }
        for record in self:
            record.priorite_ligne_commande = priority_mapping.get(record.type_ligne_commande, 0)

    @api.depends('date_planned_start')
    def _compute_priorite_date_livraison(self):
        for record in self:
            if record.delivery_date:
                days_until_due = (record.delivery_date - datetime.today()).days
                if days_until_due < 0:
                    record.priorite_date_livraison = 0
                else:
                    record.priorite_date_livraison = max(100 - days_until_due, 0)

    # @api.depends('workorder_ids.workcenter_id.default_capacity')
    # def _compute_priorite_capacite(self):
    #     for record in self:
    #         capacity_priority = 0
    #         for workorder in record.workorder_ids:
    #             if workorder.workcenter_id.default_capacity > workorder.qty_remaining:
    #                 capacity_priority = 100
    #                 break
    #         record.priorite_capacite = capacity_priority

    @api.depends('priorite_ligne_commande', 'priorite_date_livraison')
    def _compute_priorite_globale(self):
        for record in self:
            record.priorite_globale = (record.priorite_ligne_commande + record.priorite_date_livraison) / 2

    priorite_categorie = fields.Selection([
        ('P1', 'P1'),
        ('P2', 'P2'),
        ('P3', 'P3')
    ], string="Catégorie de Priorité", compute="_compute_priorite_categorie", help="P1 (0-40) , P2 (41-69), P3 (70-100)",
        store=True)

    @api.depends('priorite_globale')
    def _compute_priorite_categorie(self):
        for record in self:
            if record.priorite_globale <= 40:
                record.priorite_categorie = 'P1'
            elif 41 <= record.priorite_globale <= 69:
                record.priorite_categorie = 'P2'
            elif record.priorite_globale >= 70:
                record.priorite_categorie = 'P3'

    @api.model
    def create(self, vals):
        if vals.get('origin') and vals.get('product_id'):
            # Trouver toutes les lignes de commande correspondant à l'ordre et au produit
            sale_order_lines = self.env['sale.order.line'].search([
                ('order_id.name', '=', vals['origin']),
                ('product_id', '=', vals['product_id'])
            ])

            # Si plusieurs lignes sont trouvées, ajoutez une logique pour choisir la bonne
            if sale_order_lines:
                # Par exemple, choisir la ligne avec la quantité restante la plus élevée
                sale_order_line = \
                sale_order_lines.sorted(key=lambda line: line.product_uom_qty - line.qty_delivered, reverse=True)[0]
                vals['sale_order_line_id'] = sale_order_line.id
            else:
                vals['sale_order_line_id'] = False

        return super(MrpProduction, self).create(vals)

    delivery_date = fields.Datetime(string="Date de fin de traitement", compute='_compute_delivery_date')

    @api.depends('product_id.days_to_prepare_mo', 'date_planned_start', 'sale_order_line_id.date_recale',
                 'sale_order_line_id.date_livraison')
    def _compute_delivery_date(self):
        for record in self:
            final_date = False

            # Vérifiez d'abord la ligne de commande liée
            if record.sale_order_line_id:
                # Vérifiez si une date_recale est définie
                if record.sale_order_line_id.date_recale:
                    final_date = record.sale_order_line_id.date_recale
                # Sinon, vérifiez si une date_livraison est définie
                elif record.sale_order_line_id.date_livraison:
                    final_date = record.sale_order_line_id.date_livraison

            # Si aucune date spécifique n'est trouvée, appliquez le calcul habituel
            if not final_date and record.date_planned_start and record.product_id.days_to_prepare_mo:
                final_date = self.env['sale.order.line']._calculate_final_date(
                    record.date_planned_start,
                    ((record.product_id.days_to_prepare_mo + record.product_id.produce_delay)
                     if record.product_id.sale_delay == 0
                     else (record.product_id.sale_delay + record.product_id.produce_delay))
                )

            # Assigner la date finale
            record.delivery_date = final_date or record.date_planned_start

class OrdreFabrication(models.Model):
    _inherit = 'mrp.workorder'
    _order = 'priorite_globale desc, priorite_capacite desc'

    ref_prog_automate = fields.Char(string="Référence programme automate", related="operation_id.ref_prog_automate", store=True)
    matiere = fields.Many2one(string="Matière", related="production_id.bom_id.matiere", store=True)
    priorite_globale = fields.Float(string="Priorité Globale", related="production_id.priorite_globale", store=True)
    priorite_categorie = fields.Selection([
        ('P1', 'P1'),
        ('P2', 'P2'),
        ('P3', 'P3')
    ], related="production_id.priorite_categorie", store=True)
    priorite_capacite = fields.Integer(string="Priorité Capacité", compute="_compute_priorite_capacite", store=True)
    default_capacity = fields.Float(string="capacité", store=True)

    # @api.depends('default_capacity','qty_remaining')
    def _compute_priorite_capacite(self):
        for record in self:

            if record.default_capacity > record.qty_remaining:
                record.priorite_capacite = 100
            else:
                record.priorite_capacite = 4





