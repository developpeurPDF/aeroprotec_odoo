from odoo import api, fields, models, _
from math import pi
from collections import defaultdict
from odoo.exceptions import UserError, ValidationError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.constrains('product_tmpl_id')
    def _check_unique_bom_per_product_template(self):
        for bom in self:
            product_template = bom.product_tmpl_id
            if not product_template.allow_multiple_boms:
                existing_bom = self.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', product_template.id),
                    ('id', '!=', bom.id)
                ])
                if existing_bom:
                    raise ValidationError(
                        _('A BOM already exists for this product template and only one BOM is allowed.'))

    name = fields.Char(string="Libellé de nomenclature", tracking=True)
    operation_ids = fields.One2many('mrp.routing.workcenter', 'bom_id', 'Operations', copy=True, ondelete="cascade")
    code = fields.Char('Reference',compute='_compute_code' )
    modele = fields.Char(string="Modèle de nomenclature", tracking=True)
    donneur_order = fields.Many2one('donneur.order',related="product_tmpl_id.donneur_order", string="Donneur d'ordre", tracking=True)
    indice = fields.Char(string="Indice", related="product_tmpl_id.indice", tracking=True)
    norme = fields.Many2one('norme',string="Norme", tracking=True)
    nom_donneur_order = fields.Char(string="Nom du Donneur d'ordre", related='donneur_order.name.name', readonly=True)
    codes = fields.Many2one('donneur.ordre.code', string="Code traitement" , domain= "[('name_donneur_order', '=', nom_donneur_order)]", tracking=True )
    nb_traitement_surface = fields.Integer(string="Nombre de traitement de surface")
    produce_delay = fields.Float(
        'Durée du cycle', default=0.0,
        help="Average lead time in days to manufacture this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added. In case the product is subcontracted, this can be used to determine the date at which components should be sent to the subcontractor.")
    type_gamme = fields.Selection([
        ('production', 'GAMME DE PRODUCTION'),
        ('reprise', 'GAMME DE REPRISE'), ('epouvettes', 'GAMME DES ARTICLES EPOUVETTES')], 'Type de gamme',
        )
    cycle_negocie = fields.Float('Cycle négocié', default=0.0,)
    @api.onchange('mrp_bom_temp_id')
    def _onchange_mrp_bom_temp_id(self):
        if self.mrp_bom_temp_id:
            self.produce_delay = self.mrp_bom_temp_id.produce_delay
            self.famille_matiere = self.mrp_bom_temp_id.famille_matiere
            self.famille_matiere_name = self.mrp_bom_temp_id.famille_matiere_name
            self.matiere = self.mrp_bom_temp_id.matiere
            self.matiere_abreviation = self.mrp_bom_temp_id.matiere_abreviation
            self.matiere_name = self.mrp_bom_temp_id.matiere_name
            self.ref_matiere = self.mrp_bom_temp_id.ref_matiere
            self.ref_matiere_name = self.mrp_bom_temp_id.ref_matiere_name
            self.resistance_matiere = self.mrp_bom_temp_id.resistance_matiere
        else:
            self.produce_delay = 0.0
            self.famille_matiere = ""
            self.famille_matiere_name = ""
            self.matiere = ""
            self.matiere_abreviation = ""
            self.matiere_name = ""
            self.ref_matiere = ""
            self.ref_matiere_name = ""
            self.resistance_matiere = ""


    state = fields.Selection(
        selection=[
            ('brouillon', 'Brouillon'),
            ('redige', 'Rédigé'),
            ('verifie', 'Vérifié'),
            ('approve', 'Approuvé'),
            ('active', 'Active'),
        ],
        string='Status',
        copy=False,
        tracking=True,
        default='brouillon',
    )

    def _default_employee(self):
        return self.env.user.employee_id

    redacteur = fields.Many2one('res.partner', string="Rédacteur", default=_default_employee, tracking=True)
    date_redaction = fields.Datetime( string="Date de rédaction", tracking=True)
    verificateur = fields.Many2one('res.partner', string="Vérificateur", default=_default_employee, tracking=True)
    date_verification = fields.Datetime(string="Date de vérification")
    approbateur = fields.Many2one('res.partner', string="Approbateur ", default=_default_employee, tracking=True)
    date_approbation = fields.Datetime(string="Date d'approbation", tracking=True)
    is_locked = fields.Boolean(string="Locked", help="Check this box to lock product modifications.")

    def reset_draft(self):
        self.write({'state': 'brouillon'})

    def action_redige(self):
        self.write({'state': 'redige'})

    def action_verifie(self):
        self.write({'state': 'verifie'})

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_active(self):
        self.write({'state': 'active'})
        self.ensure_one()
        self.is_locked = not self.is_locked
        return True

    @api.depends('product_tmpl_id.indice', 'codes.name', 'norme.indice')
    def _compute_code(self):
        for rec in self:
            # Récupération des codes avec vérification de valeur nulle
            product_code = rec.product_tmpl_id.indice or ''
            product_default_code = rec.product_tmpl_id.client.code_abreviation or ''
            product_plan_reference = rec.product_tmpl_id.plan_reference or ''
            product_donneur_order = rec.product_tmpl_id.donneur_order.name.name or ''
            product_famille_matiere = rec.product_tmpl_id.famille_matiere.name or ''
            product_abreviation_matiere = rec.product_tmpl_id.matiere_abreviation or ''
            standard_code = rec.codes.name or ''
            treatment_code = rec.norme.indice or ''

            # Récupération des abréviations d'opérations
            operation_abbrs = '-'.join(op.abreviation_operation for op in rec.operation_ids if op.abreviation_operation)

            # Génération de la référence en utilisant le code de produit, le code de norme, le code de traitement et les abréviations des opérations
            reference = f"{product_plan_reference}-{product_donneur_order}-{product_famille_matiere} {product_abreviation_matiere}-{operation_abbrs}"

            # Assignation de la référence au champ 'code'
            rec.code = reference

    code_opr = fields.Char("Code opération", compute="_compute_code_opr")
    @api.depends('product_tmpl_id.indice', 'codes.name', 'norme.indice')
    def _compute_code_opr(self):
        for rec in self:
            lines = []
            # Adding a header for the table
            header = f"{'Code opération':<20} {'Norme interne':<30} {'Norme externe':<30}"
            lines.append(header)
            lines.append('-' * 80)  # Separator line

            # Creating table rows
            for op in rec.operation_ids:
                operation_code = op.code_operation if op.code_operation else ""
                norme_interne = f"{op.norme_interne.name} indice {op.norme_interne.indice}" if op.norme_interne else ""
                norme_externe = f"{op.norme_externe.name} indice {op.norme_externe.indice}" if op.norme_externe else ""
                # Formatting each line with fixed-width columns
                line = f"{operation_code:<20} {norme_interne:<30} {norme_externe:<30}"
                lines.append(line)

            # Joining all lines with newline for display
            reference = "\n".join(lines)
            rec.code_opr = reference

    norme_interne = fields.Char("Norme Interne", compute="_compute_norme_interne")

    @api.depends('operation_ids.norme_interne')
    def _compute_norme_interne(self):
        for rec in self:
            norme_internes = ' / '.join(
                f"{op.norme_interne.name} : {op.norme_interne.indice}"
                for op in rec.operation_ids
                if op.norme_interne
            )
            rec.norme_interne = norme_internes

    norme_externe = fields.Char("Norme Interne", compute="_compute_norme_externe")



    @api.depends('operation_ids.norme_externe')
    def _compute_norme_externe(self):
        for rec in self:
            norme_externes = ' / '.join(
                f"{op.norme_externe.name} indice {op.norme_externe.indice}"
                for op in rec.operation_ids
                if op.norme_externe
            )
            rec.norme_externe = norme_externes


    evolution = fields.Boolean(string="Evolution Effectué", default=False, readonly=True)
    reference_premier_document = fields.Many2one('mrp.bom', string="Référence du premier document", copy=False,
                                                 readonly=True)
    date_derniere_duplication = fields.Datetime(string="Date de dernière duplication", copy=False, readonly=True)

    @api.model
    def duplicate_bom(self, bom_id):

        bom_original = self.browse(bom_id)
        # num_duplications = self.search_count([('reference_document_duplicated', '=', bom_original.id)])

        # Créer une copie du produit
        product_copy_data = {
            'name': f"{bom_original.product_tmpl_id.name} V2",
            'type': bom_original.product_tmpl_id.type,
            'default_code': bom_original.product_tmpl_id.default_code,
            'categ_id': bom_original.product_tmpl_id.categ_id.id,
            'allow_multiple_boms': bom_original.product_tmpl_id.allow_multiple_boms,
            'plan_reference': bom_original.product_tmpl_id.plan_reference,
            'forme': bom_original.product_tmpl_id.forme,
            'hauteur': bom_original.product_tmpl_id.hauteur,
            'largeur': bom_original.product_tmpl_id.largeur,
            'longueur': bom_original.product_tmpl_id.longueur,
            'diametre': bom_original.product_tmpl_id.diametre,
            'surface_traiter': bom_original.product_tmpl_id.surface_traiter,
            # 'type_montage': bom_original.product_tmpl_id.type_montage,
            'type_article': bom_original.product_tmpl_id.type_article,
            'famille_matiere': bom_original.product_tmpl_id.famille_matiere,
            'matiere': bom_original.product_tmpl_id.matiere,
            'matiere_abreviation': bom_original.product_tmpl_id.matiere_abreviation,
            'matiere_name': bom_original.product_tmpl_id.matiere_name,
            'ref_matiere': bom_original.product_tmpl_id.ref_matiere,
            'ref_matiere_name': bom_original.product_tmpl_id.ref_matiere_name,
            'resistance_matiere': bom_original.product_tmpl_id.resistance_matiere,
            'coeff_avion': bom_original.product_tmpl_id.coeff_avion,
            'masque_impression': bom_original.product_tmpl_id.masque_impression,
            'info_marquer': bom_original.product_tmpl_id.info_marquer,
            'n_ft': bom_original.product_tmpl_id.n_ft,
            'piece_jointe_ft': bom_original.product_tmpl_id.piece_jointe_ft,
            'norme_douaniere': bom_original.product_tmpl_id.norme_douaniere,
            'indice': bom_original.product_tmpl_id.indice,
            # 'nb_piece_barre': bom_original.product_tmpl_id.nb_piece_barre,
            'type_indice': bom_original.product_tmpl_id.type_indice,
            'donneur_order': bom_original.product_tmpl_id.donneur_order,
            'client': bom_original.product_tmpl_id.client,
            'memo': bom_original.product_tmpl_id.memo,
            'activite': bom_original.product_tmpl_id.activite,
            'motif_blocage_lancement': bom_original.product_tmpl_id.motif_blocage_lancement,
            'classe_fonctionnelle': bom_original.product_tmpl_id.classe_fonctionnelle,
            'programme_aeonautique': bom_original.product_tmpl_id.programme_aeonautique,
            'gerer_stock': bom_original.product_tmpl_id.gerer_stock,
            'gestion_lots': bom_original.product_tmpl_id.gestion_lots,
            'gestion_sortie_auto': bom_original.product_tmpl_id.gestion_sortie_auto,
            # 'route_ids': bom_original.product_tmpl_id.route_ids,
            # Copiez d'autres champs de produit selon vos besoins
        }
        new_product = self.env['product.template'].create(product_copy_data)

        # Copiez les routes
        routes_data = []
        for route in bom_original.product_tmpl_id.route_ids:
            routes_data.append((4, route.id))

        # Ajoutez les données des routes à la copie du produit
        new_product.write({'route_ids': routes_data})

        bom_copy_data = {
            'name': f"{bom_original.name} V2",
            'modele': bom_original.modele,
            'donneur_order': bom_original.donneur_order.id,
            'indice': bom_original.indice,
            # 'norme': bom_original.norme.id,
            'product_tmpl_id': new_product.id,  # Utiliser la nouvelle copie du produit

            'state': 'brouillon',  # Vous pouvez définir l'état initial ici
            'date_redaction': False,  # Réinitialiser la date de rédaction
            'date_verification': False,  # Réinitialiser la date de vérification
            'date_approbation': False,  # Réinitialiser la date d'approbation
            'is_locked': False,  # Réinitialiser l'état de verrouillage
            'reference_premier_document': bom_original.id,  # Réinitialiser la référence du premier document
            'date_derniere_duplication': fields.Datetime.now(),
            'evolution': False,
        }

        # Créer la copie
        new_bom = self.create(bom_copy_data)
        for bom_line in bom_original.bom_line_ids:
            bom_line_copy_data = {
                'bom_id': new_bom.id,
                'product_id': bom_line.product_id.id,
                'product_qty': bom_line.product_qty,
                'product_uom_id': bom_line.product_uom_id.id,
                'operation_id': bom_line.operation_id.id if bom_line.operation_id else False,
            }
            self.env['mrp.bom.line'].create(bom_line_copy_data)

        for operation in bom_original.operation_ids:
            operation_copy_data = {
                'bom_id': new_bom.id,
                'name': operation.name,
                'workcenter_id': operation.workcenter_id.id,
                'time_cycle': operation.time_cycle,
                'sequence': operation.sequence,
            }
            self.env['mrp.routing.workcenter'].create(operation_copy_data)


        bom_original.write({'evolution': True})

        return {
            'name': _('Duplicate BoM'),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'mrp.bom',
            'res_id': new_bom.id,
            'type': 'ir.actions.act_window',
        }

    famille_matiere = fields.Many2one('matiere.parameter', string="Famille matière", tracking=True, domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    # matiere = fields.Many2one('matiere.parameter', string="Famille matière")
    famille_matiere_name = fields.Char("Nom famille matière", related="famille_matiere.name", readonly=True, store=True)
    matiere = fields.Many2one('matiere.parameter.value', string="Matière",
                           domain="[('parameter_name','=', famille_matiere_name)]", tracking=True)
    matiere_abreviation = fields.Char(string="Abréviation matière", related="matiere.name_abreviation", readonly=True, store=True)
    matiere_name = fields.Char(string="Nom matière", related="matiere.name", readonly=True, store=True)
    ref_matiere = fields.Many2one('matiere.parameter.ref', string="Nature matière",
                           domain="[('parameter_name','=', matiere_name)]", tracking=True)
    ref_matiere_name = fields.Char(string="Nom matière", related="ref_matiere.name", readonly=True, store=True)
    resistance_matiere = fields.Char(string="Résistance matière", related="ref_matiere.name_resistance", tracking=True)