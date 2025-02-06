from odoo import api, fields, models, tools
from datetime import timedelta 

class ListeApplicationPeinture(models.Model):
    _inherit = 'mrp.workorder'

    state = fields.Selection(
        selection_add=[
            ('nci_waiting', 'Attente de traitement NCI')
        ],
        ondelete={'nci_waiting': 'set default'}
    )
    sous_op = fields.Many2many(
        'phase.operation',
        related='operation_id.phase',
        string="Sous opérations"
    )
    gamme_of = fields.Many2one(
        'mrp.bom',
        related='production_id.bom_id',
        string="Gamme"
    )

    type_of = fields.Selection(
        related='production_id.type_of',
        string="Type OF",
        readonly=True,
    )
   
    client = fields.Many2one(
        'res.partner',
        related='production_id.sale_order_line_id.order_partner_id',
        string="Client",
        readonly=True,
    )
    ref_commande_interne = fields.Char(
        related='production_id.sale_order_line_id.order_id.name',
        string="CMD Int",
        readonly=True,
    )
    ref_commande_client = fields.Char(
        related='production_id.sale_order_line_id.order_id.client_order_ref',
        string="CMD Clt",
        readonly=True,
    )

    n_poste = fields.Char(
        related='production_id.sale_order_line_id.n_poste_client',
        string="N° Poste",
        readonly=True,
    )
    aog = fields.Selection(
        related='production_id.sale_order_line_id.type_ligne',
        string="Type ligne",
        readonly=True,
    )
    fai = fields.Boolean(
        related='production_id.sale_order_line_id.fai',
        string="FAI",
        readonly=True,
    )
    reference_piece = fields.Char(related='product_id.default_code', string="Réf de la pièce")
    designation_piece = fields.Char(related='product_id.name', string="Désignation")
    phase_precedente = fields.Char(
    compute='_compute_previous_workorder', 
    string="Phase Précédente"
    )


    @api.depends('production_id', 'state', 'date_finished')
    def _compute_previous_workorder(self):
        for workorder in self:
            workorder.phase_precedente = ""
            #if not workorder.production_id or not workorder.date_finished:
                #continue
            previous_workorder = self.env['mrp.workorder'].search([
                ('production_id', '=', workorder.production_id.id),
                ('id', '!=', workorder.id),
                ('state', '=', 'done'),
                #('date_finished', '<', workorder.date_finished)
            ], order='date_finished desc', limit=1)

            if previous_workorder:
                workorder.phase_precedente = previous_workorder.name

        
       
    heures_sans_activite = fields.Float(
    string="H ss activité", 
    compute='_compute_heures_sans_activite'
    )
    @api.depends('date_start', 'production_id')
    def _compute_heures_sans_activite(self):
        for workorder in self:
            workorder.heures_sans_activite = 0.0
            if not workorder.date_start:
                continue
            previous_workorder = self.env['mrp.workorder'].search([
                ('production_id', '=', workorder.production_id.id),
                ('id', '!=', workorder.id),
                ('state', '=', 'done'),
                ('date_start', '<', workorder.date_start)
            ], order='date_start desc', limit=1)
            if previous_workorder and previous_workorder.date_start and previous_workorder.duration:
                previous_end_time = previous_workorder.date_start + timedelta(hours=previous_workorder.duration)

                delta = workorder.date_start - previous_end_time
                workorder.heures_sans_activite = abs(delta.total_seconds() / 3600)
  

    jours_sans_activite = fields.Float(string="J ss activité", compute="_compute_jours_sans_activite")
    @api.depends('heures_sans_activite')
    def _compute_jours_sans_activite(self):
        for workorder in self:
            workorder.jours_sans_activite = workorder.heures_sans_activite / 24
    
    date_demarrage_theorique = fields.Datetime(related='production_id.date_planned_start', string="Date début Th")
    date_dernier_pointage = fields.Datetime(related='production_id.sale_order_line_id.last_mo_date', string="D et H der pointage")
    #matricule_operateur = fields.Char(related='production_id.sale_order_line_id.order_partner_id.employee_ids.identification_id', string="Mat Opérateur")
    #matricule_operateur = fields.Char(related='time_ids.user_id.employee_ids.matricule', string="Mat Opérateur")
    matricule_operateur = fields.Char(
    string="Mat Opérateur",
    compute="_compute_matricule_operateur"
    )
    nom_operateur = fields.Char(
    string="Nom Opérateur",
    compute="_compute_matricule_operateur",
    store=True
    )
    @api.depends('time_ids.user_id.employee_ids.matricule')
    def _compute_matricule_operateur(self):
        for record in self:
            if record.time_ids:
                latest_time = record.time_ids.sorted('create_date', reverse=True)[:1]
                if latest_time:
                    latest_user = latest_time.user_id
                    if latest_user and latest_user.employee_ids:
                        employee = latest_user.employee_ids[:1]
                        record.matricule_operateur = employee.matricule if employee.matricule else False
                        record.nom_operateur = employee.name if employee.name else False
                    else:
                        record.matricule_operateur = False
                        record.nom_operateur = False
                else:
                    record.matricule_operateur = False
                    record.nom_operateur = False
            else:
                record.matricule_operateur = False
                record.nom_operateur = False
   
    date_livraison_theorique = fields.Datetime(related='production_id.sale_order_line_id.date_livraison', string="D livraison")

    temps_theorique = fields.Float(related='production_id.production_duration_expected', string="Temps Th")
    #nb_pieces_restantes = fields.Integer(string="Nb de pièces restantes")
    #nb_pieces_totales = fields.Integer(string="Nb de pièces totales sur la phase")
    code_barre_phase = fields.Char(string="Code barre phase")

    photo_piece = fields.Binary(related='product_id.image_1920', string="Photo")
    longueur_piece = fields.Float(related='product_id.longueur', string="Longueur pièce")

    abreviation_matiere = fields.Char(string="Ab matière", compute="_compute_matiere_details")
    famille_matiere = fields.Char(string="Famille matière", compute="_compute_matiere_details")
    ref_matiere = fields.Char(string="Réf matière", compute="_compute_matiere_details")
    resistance_matiere = fields.Char(string="Résistance matière", compute="_compute_matiere_details")
    @api.depends('product_id.matiere_abreviation', 'product_id.famille_matiere', 'product_id.ref_matiere', 'product_id.resistance_matiere')
    def _compute_matiere_details(self):
        for record in self:
            record.abreviation_matiere = record.product_id.matiere_abreviation or ''
            record.famille_matiere = record.product_id.famille_matiere or ''
            record.ref_matiere = record.product_id.ref_matiere or ''
            record.resistance_matiere = record.product_id.resistance_matiere or ''

    applications_ids = fields.One2many('application.peinture', 'workorder_id', string="applications peintures")
    etuvage_ids = fields.One2many('etuvage', 'workorder_id', string="Etuvage")

    def create_maintenance_request(self):
        MaintenanceRequest = self.env['maintenance.request']
        MaintenanceTeam = self.env['maintenance.team'].search([], limit=1)

        if not MaintenanceTeam:
            MaintenanceTeam = self.env['maintenance.team'].create({
                'name': 'Équipe de Maintenance Par Défaut',
            })

        for workorder in self:

            QualityPoint = self.env['quality.point.equipement'].search([], limit=1)
            if not QualityPoint:
                QualityPoint = self.env['quality.point.equipement'].create({
                    'name': 'Point de Qualité Par Défaut',
                })

            maintenance_request = MaintenanceRequest.create({
                'name': f'Maintenance pour {workorder.name}',
                'request_date': fields.Datetime.now(),
                'maintenance_team_id': MaintenanceTeam.id,
                'quality_point_id': QualityPoint.id,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Maintenance Request',
                'res_model': 'maintenance.request',
                'view_mode': 'form',
                'res_id': maintenance_request.id,
                'target': 'current',
            }

