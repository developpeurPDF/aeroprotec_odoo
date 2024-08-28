from odoo import api, fields, models


class QualityControl(models.Model):
    _name = 'quality.control'
    _description = 'Contrôle de Qualité'

    name = fields.Many2one('product.product', string="Produit Reçu")
    move_id = fields.Many2one('stock.move', string="Ligne de Mouvement", required=True)
    prix = fields.Float(string="Prix dans le bon de commande ")
    value_prix = fields.Float(string="Prix reçu")
    state_prix = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    quantite = fields.Float(string="Quantité dans le bon de commande ")
    value_quantite = fields.Float(string="Quantité reçue")
    state_quantite = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    delai = fields.Float(string="Délai dans le bon de commande ")
    value_delai = fields.Float(string="Délai reçu")
    state_delai = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    changement_indice = fields.Float(string="Changement indice")
    value_changement_indice = fields.Float(string="Changement indice reçu")
    state_changement_indice = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    changement_traitement = fields.Char(string="Changement de traitement")
    value_changement_traitement = fields.Char(string="Changement de traitement reçu")
    state_changement_traitement = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    ecart = fields.Float(string="Écart demande client et gamme")
    value_ecart = fields.Float(string="Écart demande client et gamme reçu")
    state_ecart = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")

    etat_piece = fields.Selection([('bon', 'Bon'), ('Mauvais', 'Non')], string="Etat Pièce", default='bon')
    value_etat_piece = fields.Selection([('bon', 'Bon'), ('Mauvais', 'Non')], string="Etat pièce reçu")
    state_etat_piece = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Conforme")
    photo_etat_piece = fields.Binary(string="Photo de l'état de la pièce")

    conforme = fields.Selection([('conforme', 'Produit Conforme'), ('non_conforme', 'Produit non conforme')],
                                string="Conformité du produit reçu",
                                compute="compute_conformite",
                                store=True)

    @api.depends('state_prix', 'state_quantite', 'state_delai', 'state_changement_indice',
                 'state_changement_traitement', 'state_ecart')
    def compute_conformite(self):
        for rec in self:
            if (rec.state_prix == "oui" and rec.state_quantite == "oui" and rec.state_delai == "oui" and
                    rec.state_changement_indice == "oui" and rec.state_changement_traitement == "oui" and rec.state_ecart == "oui"):
                rec.conforme = 'conforme'
            else:
                rec.conforme = 'non_conforme'
