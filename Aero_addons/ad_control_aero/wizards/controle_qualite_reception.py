

from odoo import api, fields, models, _


class ControlTableWizard(models.TransientModel):
    _name = 'control.table.wizard'
    _description = 'Contrôle de Qualité'

    name = fields.Many2one('product.product', string="Produit Reçu")
    move_id = fields.Many2one('stock.move', string="Ligne de Mouvement", required=True)


    # picking_id = fields.Many2one('stock.move', string="Picking")
    prix = fields.Float(string="Prix dans le bon de commande ")
    value_prix = fields.Float(string="Prix reçu")
    state_prix = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    quantite = fields.Float(string="Quantité dans le bon de commande ")
    value_quantite = fields.Float(string="Quantité reçu")
    state_quantite = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")


    delai = fields.Float(string="Délai dans le bon de commande ")
    value_delai = fields.Float(string="Délai")
    state_delai = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    changement_indice = fields.Float(string="Changement indice")
    value_changement_indice = fields.Float(string="Changement indice reçu")
    state_changement_indice = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    changement_traitement = fields.Float(string="Changement de traitement")
    value_changement_traitement = fields.Char(string="Changement de traitement reçu")
    state_changement_traitement = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    ecart = fields.Float(string="Ecart demande client et gamme")
    value_ecart = fields.Float(string="Ecart demande client et gamme")
    state_ecart = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    etat_piece = fields.Selection([('bon', 'Bon'), ('Mauvais', 'Non')], string="Etat Pièce", default='bon')
    value_etat_piece = fields.Selection([('bon', 'Bon'), ('Mauvais', 'Non')], string="Etat pièce reçu")
    state_etat_piece = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")
    photo_etat_piece = fields.Binary(string="Photo de l'état de la pièce")


    conforme = fields.Selection([('conforme', 'Produit Conforme'), ('non_conforme', 'Produit non conforme')],
                                string="Conformité de produit reçu",
                                compute="compute_conformite")

    @api.model
    def default_get(self, fields):
        res = super(ControlTableWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        if active_id:
            selected_record = self.env['stock.move'].browse(active_id)
            if selected_record:
                res['name'] = selected_record.product_id.id
                res['move_id'] = selected_record.id
                res['prix'] = selected_record.sale_line_id.price_unit
                res['quantite'] = selected_record.sale_line_id.product_uom_qty

        return res

    @api.depends('state_prix', 'state_quantite', 'state_delai', 'state_changement_indice',
                 'state_changement_traitement', 'state_ecart')
    def compute_conformite(self):
        for rec in self:
            if (rec.state_prix == "oui" and rec.state_quantite == "oui" and rec.state_delai == "oui" and
                    rec.state_changement_indice == "oui" and rec.state_changement_traitement == "oui" and rec.state_ecart == "oui"):
                rec.conforme = 'conforme'
            else:
                rec.conforme = 'non_conforme'

    def save_quality_control(self):
        """Save the quality control results and update the stock move"""
        self.ensure_one()
        if self.move_id:
            # Create the quality control record and link it to the stock move
            control_record = self.env['quality.control'].create({
                'name': self.name.id,
                'move_id': self.move_id.id,
                'prix': self.prix,
                'value_prix': self.value_prix,
                'state_prix': self.state_prix,
                'quantite': self.quantite,
                'value_quantite': self.value_quantite,
                'state_quantite': self.state_quantite,
                'delai': self.delai,
                'value_delai': self.value_delai,
                'state_delai': self.state_delai,
                'changement_indice': self.changement_indice,
                'value_changement_indice': self.value_changement_indice,
                'state_changement_indice': self.state_changement_indice,
                'changement_traitement': self.changement_traitement,
                'value_changement_traitement': self.value_changement_traitement,
                'state_changement_traitement': self.state_changement_traitement,
                'ecart': self.ecart,
                'value_ecart': self.value_ecart,
                'state_ecart': self.state_ecart,
                'conforme': self.conforme,
            })
            self.move_id.is_conforme = self.conforme
            self.move_id.quality_control_id = control_record.id  # Lier le contrôle au stock.move
        move = self.env['stock.move'].browse(self.move_id.id)
        move.quality_control_done = True
        return {'type': 'ir.actions.act_window_close'}
