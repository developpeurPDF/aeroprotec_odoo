from odoo import api, fields, models, tools


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'


    ph_eaux = fields.Float("Ph des eaux")
    conformite_ph_eaux = fields.Selection(selection=[('Oui', 'Oui'),('Non', 'Non'),],string="Conformité de Ph des eaux",
                                          compute='_compute_conformite_ph_eaux',
                                          store=True
                                          )

    @api.depends('ph_eaux', 'quality_point_id')
    def _compute_conformite_ph_eaux(self):
        for record in self:
            if record.quality_point_id and record.ph_eaux == record.quality_point_id.ph_eaux:
                record.conformite_ph_eaux = 'Oui'
            else:
                record.conformite_ph_eaux = 'Non'


    conformite = fields.Selection(selection=[('Oui', 'Oui'),('Non', 'Non'),],string="Conformite",)
    conductivite_eaux_rincage = fields.Float("Conductivité des eaux de rinçage")
    conformite_conductivite_eaux_rincage = fields.Selection(selection=[('Oui', 'Oui'), ('Non', 'Non'), ],string="Conformité de Conductivité des eaux de rinçage",
                                                            compute='_compute_conformite_conductivite_eaux_rincage',
                                                            store=True
                                                            )

    @api.depends('conductivite_eaux_rincage', 'quality_point_id')
    def _compute_conformite_conductivite_eaux_rincage(self):
        for record in self:
            if record.quality_point_id and record.conductivite_eaux_rincage == record.quality_point_id.conductivite_eaux_rincage:
                record.conformite_conductivite_eaux_rincage = 'Oui'
            else:
                record.conformite_conductivite_eaux_rincage = 'Non'



    aspect_bains = fields.Selection(selection=[('Oui', 'Oui'), ('Non', 'Non'), ], string="Aspect des bains",  )

    test_type = fields.Selection(
        [('pass_fail', 'Pass-Fail'), ('measure', 'Measure'), ('picture', 'Take a Picture'), ('text', 'Text'), ('suivi_bain', 'Suivi des installations bains')],
        string="Type", default='pass_fail', related="quality_point_id.test_type")

    picture = fields.Binary(string="Photo")
    quality_point_id = fields.Many2one('quality.point.equipement', string="Point de contrôle", required=True, domain="[('category_id', '=', category_id)]")

    state = fields.Selection([('do', 'To Do'), ('pass', "Pass"), ('fail', 'Fail')], default="do")
    measure = fields.Float(string="Measure")
    note = fields.Html(string="Notes", related="quality_point_id.instruction")

    norm = fields.Float('Norm')

    unit = fields.Char(related="quality_point_id.unit")
    min_quality = fields.Float('Tolerance', related="quality_point_id.min_quality")
    max_quality = fields.Float('Max', related="quality_point_id.max_quality")
    team_id = fields.Many2one('quality.team', related="quality_point_id.team_id")

    def validate_quality_check(self):
        """
        Valide le contrôle qualité en comparant les valeurs saisies dans quality.checks avec celles de quality.point.equipement
        """
        for check in self:
            # Exemple de conditions pour valider la qualité
            if check.quality_point_id.test_type == 'suivi_bain':
                if (check.ph_eaux == check.quality_point_id.ph_eaux and
                    check.conductivite_eaux_rincage == check.quality_point_id.conductivite_eaux_rincage and
                    check.aspect_bains == 'Oui' and check.conformite_ph_eaux == 'Oui'
                        and check.conformite_conductivite_eaux_rincage == 'Oui'):
                    check.state = 'pass'
                else:
                    check.state = 'fail'
            elif check.quality_point_id.test_type == 'measure':
                if (self.measure < self.min_quality or self.measure > self.max_quality):
                    check.state = 'pass'
                else:
                    check.state = 'fail'
            else:
                if check.conforme == "Oui":
                    check.state = 'pass'
                else:
                    check.state = 'fail'
