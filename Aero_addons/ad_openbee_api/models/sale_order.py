from odoo import models, fields, api
import requests
import hashlib
import os
import tempfile
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    openbee_document_id = fields.Char(string='OpenBee Document ID', readonly=True)

    def send_to_openbee(self):
        """Envoie la facture vers OpenBee via l'API REST"""
        self.ensure_one()

        # Récupération des paramètres OpenBee
        params = self.env['parametre.openbee'].search([('document_model', '=', 'sale.order')], limit=1)#.get_params()

        # Génération du PDF de la facture
        report_name = 'reports_combination.report_saleorder_cgv' #if self.invoice_payments_widget else 'account.report_invoice'
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
            'name': 'Commande_vente_' + str(self.id),
            'title': 'Commande vente',  # Ajout du champ title obligatoire
            'description': 'Commande vente' + str(self.name) + ' du ' + str(self.date_order),
            'path':   "/Commandes Ventes/"+ str(self.partner_id.name),
            # 'idParentFolder': self.partner_id.openbee_folder_sale_id,
            # 'type': params.type_id,  # ID de la catégorie "commandes ventes" dans OpenBee
            'metadatas[11388]': 'Commande vente' + str(self.id),
            'metadatas[11389]': self.partner_id.name,
            'metadatas[11390]': self.date_order.strftime('%Y-%m-%d') if self.date_order else '',
            # 'metadatas[11328]': str(self.amount_total),
            # 'metadatas[11329]': '0' if self.payment_state == 'paid' else '1',
        }
        print("self.partner_id.openbee_folder_sale_id",self.partner_id.openbee_folder_sale_id)

        # Création d'un fichier temporaire avec le module tempfile
        temp_handle, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
        try:
            # Écriture du contenu PDF dans le fichier temporaire
            with os.fdopen(temp_handle, 'wb') as pdf_file:
                pdf_file.write(pdf_content)

            # Envoi du document
            with open(temp_pdf_path, 'rb') as pdf_file:
                files = {
                    'file': ('commande_vente.pdf', pdf_file, 'application/pdf')
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