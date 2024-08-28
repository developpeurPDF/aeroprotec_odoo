from odoo import api, fields, models, _
from math import pi

class PhaseOperation(models.Model):
    _name = 'phase.operation'

    ordre = fields.Integer(string="Ordre")
    name = fields.Char(string="Sous opérations",required=True,)
    code = fields.Char(string="Code")

    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)
    operations = fields.Many2one('mrp.routing.workcenter', string="Opérations")
    note = fields.Html(string="Note")

class NatureOperation(models.Model):
    _name = 'nature.operation'

    name = fields.Char(string="Nature d'opération", required=True, )
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)


class MrpRoutingWorkcenter(models.Model):
    _name = 'mrp.routing.workcenter'
    _inherit = ['mrp.routing.workcenter', 'mail.thread', 'mail.activity.mixin']

    standard_operations = fields.Boolean(string="Operation Standard", default=False)
    nb_piece_barre = fields.Integer(string="Nombre de pièces par barre", tracking=True)
    type_montage = fields.Selection(selection=[
        ('CADRE_SIMPLE', 'CADRE SIMPLE'),
        ('CADRE_DOUBLE', 'CADRE DOUBLE'),
        ('MONTAGE_TOURNANT', 'MONTAGE TOURNANT'),
    ],
        string='Type de montage', tracking=True)


    def copy_to_bom(self):
        print("nonnnn")
        if 'bom_id' in self.env.context:
            print("self.env.contextcontext", self.env.context)
            print("noooooooooooooonnnn")
            bom_id = self.env.context.get('bom_id')
            for operation in self:
                # Copier l'opération avec le champ standard_operations toujours à False
                operation.copy({
                    'bom_id': bom_id,
                    'standard_operations': False,  # Forcer le champ standard_operations à False
                })
            return {
                'view_mode': 'form',
                'res_model': 'mrp.bom',
                'views': [(False, 'form')],
                'type': 'ir.actions.act_window',
                'res_id': bom_id,
            }
        # Assure qu'il n'y a qu'un seul enregistrement
        print("self.env.context",self.env.context)
        print("self.env.context.get('bom_temp_id')",self.env.context.get('bom_temp_id'))
        if 'bom_temp_id' in self.env.context:
            print("yesssssssssssss")
            bom_temp_id  = self.env.context.get('bom_temp_id')
            copied_operations = []
            for operation in self:
                # Copier l'opération avec le champ standard_operations toujours à False

                # Copier l'opération avec le champ standard_operations toujours à False
                copied_operation = operation.copy({
                    'bom_temp_id': bom_temp_id,
                    'standard_operations': False,
                    })
                copied_operations.append(copied_operation)

                # Récupérer le modèle mrp.bom.template correspondant à l'ID bom_temp_id
            bom_template = self.env['mrp.bom.template'].browse(bom_temp_id)
            # Ajouter les opérations copiées au champ operation_ids du modèle mrp.bom.template
            bom_template.write({
                'operation_ids': [(4, copied_op.id) for copied_op in copied_operations]
            })
            return {
                'name': _('Copied Operations'),
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'mrp.bom.template',
                'res_id': bom_temp_id,
                'type': 'ir.actions.act_window',

            }


    def copy_existing_operations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Copier les opérations existantes'),
            'res_model': 'mrp.routing.workcenter',
            'view_mode': 'tree,form',
            'domain': ['|', ('bom_id', '=', False), ('bom_id.active', '=', True), ('standard_operations', '=', True)],
            'context': {
                'bom_id': self.env.context["bom_id"],
                'tree_view_ref': 'mrp.mrp_routing_workcenter_copy_to_bom_tree_view',
            }
        }

    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id, related=False)
    nature_operation = fields.Many2one('nature.operation', string="Nature d'opérations", tracking=True)
    phase = fields.Many2many('phase.operation', string="Sous opérations", tracking=True)

    norme_interne = fields.Many2one('norme', string="Norme Interne",
                                    domain=[('type_norme', '=', 'interne'),
                                            ('state', 'in', ['conforme', 'derogation'])],
                                    tracking=True)
    norme_externe = fields.Many2one('norme', string="Norme Externe",
                                    domain=[('type_norme', '=', 'externe'),
                                            ('state', 'in', ['conforme', 'derogation'])],
                                    tracking=True)
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        index=True, ondelete='cascade', required=False, check_company=True)
    ref_prog_automate = fields.Char(string="Référence programme automate", tracking=True)
    competance = fields.Text(string="Compétences")
    abreviation_operation = fields.Char(string="Abréviation de l’opération", tracking=True)
    code_operation = fields.Char(string="Code de l’opération", tracking=True)
    type_operation = fields.Selection([
            ('prestation', 'Prestation'),
            ('traitement_surface', 'Traitement de surface'),
            ('peinture', 'Peinture'),
            ('cnd', 'CND'),
        ],
        string="Type opération",
        default='prestation', tracking=True)

    operation_ts = fields.Selection(selection=[
        ('Oui', 'Oui'),
        ('Non', 'Non')
    ], string="Opérations de TS", compute= "_compute_operation_ts")

    def _compute_operation_ts(self):
        for rec in self:
            if rec.type_operation in ["traitement_surface", "peinture"]:
                rec.operation_ts = "Oui"
            else:
                rec.operation_ts = "Non"

    capacity_ids = fields.One2many('mrp.workcenter.capacity', 'operation_ids', string='Product Capacities',
                                   help="Specific number of pieces that can be produced in parallel per product.",
                                   copy=True)


class MrpWorkCenterCapacity(models.Model):
    _inherit = 'mrp.workcenter.capacity'

    operation_ids = fields.Many2one('mrp.routing.workcenter', string='Opérations', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Poste de travail', required=True)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company.id)


    @api.onchange('operation_ids')
    def _onchange_operation_ids(self):
        if self.operation_ids:
            self.workcenter_id = self.operation_ids.workcenter_id.id