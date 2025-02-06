from odoo import api, fields, models, tools
from datetime import datetime


class ApplicationPeinture(models.Model):
    _name = 'application.peinture'
    _description = 'Application Peinture'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #ordre_fabrication = fields.Many2one('mrp.production', string="Ordre de fabrication")
    name = fields.Char("Nom", readonly=True, copy=False, tracking=True)

    quantite = fields.Integer("Qty", tracking=True)
    termine = fields.Boolean("Termine", tracking=True)
    melange = fields.Many2one('peinture.melange', string="Mélange", tracking=True)
    n_sequence = fields.Char("N° Sequence", readonly=True, copy=False, tracking=True)
    Temperature_application = fields.Char("Température", tracking=True)
    hygrometrie_application = fields.Char("Hygrometrie", tracking=True)
    date_debut = fields.Datetime("Date de début", tracking=True)
    date_fin = fields.Datetime("Date de fin", tracking=True)
    remarque_application = fields.Text("Remarques", tracking=True)
    workorder_id = fields.Many2one('mrp.workorder', string="order de travail", store=True, tracking=True)
    
    workorders_ids = fields.Many2many('mrp.workorder', string="order de travail", tracking=True)
    of_id = fields.Many2one('mrp.production', string="OF")
    #@api.model
    #def _default_workorder_id(self):
       # return self.env.context.get('default_workorder_id')

   # @api.model
   # def _default_of_id(self):
       # workorder_id = self.env.context.get('default_workorder_id')
       # if workorder_id:
           # workorder = self.env['mrp.workorder'].browse(workorder_id)
           # return workorder.production_id.name  
       # return False
    
    


    personne_id = fields.Many2one(
        'res.users', 
        string="Responsable", 
        default=lambda self: self.env.user, 
        readonly=True, tracking=True
    )
    statut = fields.Selection(
        [('en_cours', 'En cours'), ('termine', 'Terminé')], 
        string="Statut", 
        default='en_cours', 
        tracking=True
    )
    @api.onchange('statut')
    def _onchange_statut(self):
       
        if self.statut == 'termine':
            
            pass

    Temperature_etuvage = fields.Char("Température Etuvage", related='etuvage_id.Temperature_etuvage')
    #n_etuvage = fields.Float("N° Etuve")
    date_debut_etuvege = fields.Datetime("Date de début", related='etuvage_id.date_debut_etuvege')
    date_fin_etuvage = fields.Datetime("Date de fin", related='etuvage_id.date_fin_etuvage')

    remarque_etuvage = fields.Text("Remarques", related='etuvage_id.remarque_etuvage')
    etuvage_id = fields.Many2one('etuvage', string="N° Etuvage", readonly=True, tracking=True)
    etuvage_name = fields.Char(string="Etuvage Name", related='etuvage_id.name', readonly=True, tracking=True)
    def action_create_etuvage(self):

        for record in self:
            etuvage_vals = {
                #'name': f"ETV-{record.name}",  
                'workorder_id': record.workorder_id.id,
                #'Temperature_etuvage': record.Temperature_application,
                'app_peinture': record.id,
                'remarque_etuvage': f"Crée pour l'application de peinture: {record.name}",
            }
            etuvage = self.env['etuvage'].create(etuvage_vals)
            record.etuvage_id = etuvage.id

    @api.model
    def create(self, vals):
        if 'workorder_id' in vals and vals['workorder_id']:
            existing_etuvage = self.env['application.peinture'].search([
                ('workorder_id', '=', vals['workorder_id'])
            ], limit=1)

            

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        if current_month == 12:
            next_year = current_year + 1
            next_month = 1
        else:
            next_year = current_year
            next_month = current_month + 1

        count = self.env['application.peinture'].search_count([
            ('create_date', '>=', f'{current_year}-{current_month:02d}-01'),
            ('create_date', '<', f'{next_year}-{next_month:02d}-01')
        ]) + 1

        sequence = f"MP/{current_year}/{current_month:02d}/{count:03d}"
        vals['n_sequence'] = sequence

        vals['name'] = sequence

        return super(ApplicationPeinture, self).create(vals)
