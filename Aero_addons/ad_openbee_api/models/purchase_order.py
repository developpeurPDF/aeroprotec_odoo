from odoo import models, fields, api
import requests
import hashlib
import os
import tempfile


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    openbee_document_id = fields.Char(string='OpenBee Document ID', readonly=True)

    def send_to_openbee(self):
        """Envoie le bon de commande d'achat vers OpenBee via l'API REST"""
        self.ensure_one()

        # Récupération des paramètres OpenBee
        params = self.env['parametre.openbee'].search([('document_model', '=', 'purchase.order')], limit=1)

        # Génération du PDF du bon de commande d'achat
        report_name = 'purchase.report_purchaseorder'  # Vérifie que ce rapport est bien le bon
        pdf_content = self.env['ir.actions.report']._render_qweb_pdf(report_name, [self.id])[0]

        # Calcul du checksum SHA256
        checksum = hashlib.sha256(pdf_content).hexdigest()

        # Préparation des headers
        headers = {
            'OB-CHECKSUM': checksum,
            'OB-CHECKSUM-ALGO': 'sha256'
        }

        # Préparation des données du formulaire
        form_data = {
            'name': 'Bon_commande_achat_' + str(self.id),
            'title': 'Bon de Commande Achat',
            'description': 'Bon de commande ' + str(self.name) + ' du ' + str(self.date_order),
            'path': "/Commande Achat/" + str(self.partner_id.name),
            'type': params.type_id,  # ID de la catégorie "Factures" dans OpenBee
            'metadatas[11397]': 'Bon commande achat ' + str(self.id),
            'metadatas[11398]': self.partner_id.name,
            'metadatas[11399]': self.date_order.strftime('%Y-%m-%d') if self.date_order else '',
        }

        # Création d'un fichier temporaire
        temp_handle, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
        try:
            # Écriture du contenu PDF dans le fichier temporaire
            with os.fdopen(temp_handle, 'wb') as pdf_file:
                pdf_file.write(pdf_content)

            # Envoi du document
            with open(temp_pdf_path, 'rb') as pdf_file:
                files = {
                    'file': ('bon_commande_achat.pdf', pdf_file, 'application/pdf')
                }

                response = requests.post(
                    f'{params.api_url}/browse/ws/document',
                    headers=headers,
                    data=form_data,
                    files=files,
                    auth=(params.username, params.password)
                )

            if response.status_code == 200:
                result = response.json()
                self.openbee_document_id = result.get('id')
                self.message_post(body=f'Document envoyé vers OpenBee avec succès (ID: {self.openbee_document_id})')
            else:
                try:
                    response_content = response.json()
                except ValueError:
                    response_content = response.text  # Si la réponse n'est pas en JSON, récupérer le texte brut

                raise models.UserError(f'Message lors de l\'envoi vers OpenBee: {response_content}')

        finally:
            # Nettoyage du fichier temporaire
            try:
                os.unlink(temp_pdf_path)
            except Exception:
                pass
