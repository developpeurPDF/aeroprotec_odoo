from odoo import api, fields, models, tools


class QualityPointEquipement(models.Model):
    _name = 'quality.point.equipement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")


    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    # test_type = fields.Selection([('pass_fail', 'Pass-Fail'), ('measure', 'Measure')], string="Type",
    #                              default='pass_fail', required=True)
    norm = fields.Float('Norm')
    unit = fields.Char('unit')
    min_quality = fields.Float('Tolerance')
    max_quality = fields.Float('Max')
    user_id = fields.Many2one('res.users', string="Responsible")
    instruction = fields.Html(string="Instruction")
    message = fields.Html(string="Message If Fail")
    team_id = fields.Many2one('quality.team', string="Team")

    # ph_eaux = fields.Float("Ph des eaux")
    # conductivite_eaux_rincage = fields.Float("Conductivité des eaux de rinçage")

    picture = fields.Binary(string="Photo")
    test_type = fields.Selection([('pass_fail', 'Pass-Fail'), ('measure', 'Measure'), ('picture', 'Take a Picture'), ('text', 'Text') , ('suivi_bain', 'Suivi des installations bains')], string="Type",
                                 default='pass_fail', required=True)

    ph_eaux = fields.Float("Ph des eaux")
    # conformite_ph_eaux = fields.Selection(selection=[('Oui', 'Oui'), ('Non', 'Non'), ],
    #                                      string="Conformité de Ph des eaux", )
    conductivite_eaux_rincage = fields.Float("Conductivité des eaux de rinçage")
    # conformite_conductivite_eaux_rincage = fields.Selection(selection=[('Oui', 'Oui'), ('Non', 'Non'), ],
    #                                                        string="Conformité de Conductivité des eaux de rinçage", )
    # aspect_bains = fields.Selection(selection=[('Oui', 'Oui'), ('Non', 'Non'), ], string="Aspect des bains", )

    category_id = fields.Many2one('maintenance.equipment.category', string='Catégorie Equipment', tracking=True)




    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('quality.point.equipement') or '/'
        vals['name'] = seq
        return super(QualityPointEquipement, self).create(vals)