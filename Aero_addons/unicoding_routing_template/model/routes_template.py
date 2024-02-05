from odoo import api, fields, models

class BOMRouteTemplate(models.Model):
    _name='bom.route.template'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,default=lambda self: self.env.company)
    route_lines = fields.One2many('bom.route.template.line','route_id', string='Route Lines')
    note = fields.Text(string='Note')

class BOMRouteTemplateLine(models.Model):
    _name='bom.route.template.line'

    route_id = fields.Many2one('bom.route.template', string='Route', required=True)
    operation_name = fields.Char(string='Operation', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter',string='Work Center', required=True)
    sequence = fields.Integer(string='Sequence')
    time_mode = fields.Selection([
        ('auto', 'Compute based on tracked time'),
        ('manual', 'Set duration manually')], string='Duration Computation',
        default='manual')
    time_mode_batch = fields.Integer('Based on', default=10)
    time_cycle_manual = fields.Float(
        'Manual Duration', default=60,
        help="Time in minutes:"
             "- In manual mode, time used"
             "- In automatic mode, supposed first time when there aren't any work orders yet")
    worksheet_type = fields.Selection([
        ('pdf', 'PDF'), ('google_slide', 'Google Slide'), ('text', 'Text')],
        string="Work Sheet", default="text",
        help="Defines if you want to use a PDF or a Google Slide as work sheet."
    )
    note = fields.Text('Description', help="Text worksheet description")
    worksheet = fields.Binary('PDF')
    worksheet_google_slide = fields.Char('Google Slide',help="Paste the url of your Google Slide. Make sure the access to the document is public.")