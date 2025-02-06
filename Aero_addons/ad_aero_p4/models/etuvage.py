from odoo import api, fields, models, tools
from datetime import datetime
from odoo.exceptions import ValidationError


class Etuvage(models.Model):
    _name = 'etuvage'
    _description = 'Etuvage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #ordre_fabrication = fields.Many2one('mrp.production', string="Ordre de fabrication")
    name = fields.Char("Nom", readonly=True, copy=False, tracking=True)
    app_peinture = fields.Many2one('application.peinture', string="Application peinture", tracking=True)

    Temperature_etuvage = fields.Char("Température Etuvage", tracking=True)
    n_etuvage = fields.Char("N° Etuve", tracking=True)
    date_debut_etuvege = fields.Datetime("Date de début", tracking=True)
    date_fin_etuvage = fields.Datetime("Date de fin", tracking=True)
    workorder_id = fields.Many2one('mrp.workorder', string="Ordre de travail", tracking=True)

    remarque_etuvage = fields.Text("Remarques", tracking=True)

    @api.model
    def create(self, vals):
        
       # if 'workorder_id' in vals and vals['workorder_id']:
           # existing_etuvage = self.env['etuvage'].search([
               # ('workorder_id', '=', vals['workorder_id'])
           # ], limit=1)

           # if existing_etuvage:
               # raise ValidationError(_("An Etuvage record already exists for the selected work order."))

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        if current_month == 12:
            next_year = current_year + 1
            next_month = 1
        else:
            next_year = current_year
            next_month = current_month + 1

        count = self.env['etuvage'].search_count([
            ('create_date', '>=', f'{current_year}-{current_month:02d}-01'),
            ('create_date', '<', f'{next_year}-{next_month:02d}-01')
        ]) + 1

        sequence = f"ETV/{current_year}/{current_month:02d}/{count:03d}"
        vals['n_etuvage'] = sequence

        vals['name'] = sequence

        return super(Etuvage, self).create(vals)
