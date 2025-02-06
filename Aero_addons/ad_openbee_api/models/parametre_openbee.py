from odoo import models, fields, api

class ParametreOpenBee(models.Model):
    _name = 'parametre.openbee'
    _description = 'Paramètres OpenBee'

    name = fields.Char(string='Nom', required=True)
    api_url = fields.Char(string='URL API', required=True)
    username = fields.Char(string='Nom d\'utilisateur', required=True)
    password = fields.Char(string='Mot de passe', required=True)
    folder_id = fields.Char(string='ID Dossier', required=True)
    type_id = fields.Char(string='ID catégorie', required=True)
    document_model = fields.Selection([
        ('account.move', 'Factures'),
        ('sale.order', 'Commandes Clients'),
        ('purchase.order', 'Commandes Fournisseurs'),
        ('mrp.production', 'Ordres de fabrication')
    ], string='Modèle Document', required=True)

    @api.model
    def get_params(self):
        """Récupère les paramètres OpenBee"""
        params = self.search([], limit=1)
        if not params:
            raise models.UserError('Veuillez configurer les paramètres OpenBee')
        return params