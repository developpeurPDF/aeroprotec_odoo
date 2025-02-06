from odoo import models, fields, api
import requests
import hashlib
import os
import tempfile


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    openbee_document_id = fields.Char(string='OpenBee Document ID', readonly=True)

    def send_to_openbee(self):
        """Envoie le rapport d'ordre de fabrication vers OpenBee via l'API REST"""
        self.ensure_one()

        # Récupération des paramètres OpenBee spécifiques à la production
        params = self.env['parametre.openbee'].search([('document_model', '=', 'mrp.production')], limit=1)

        if not params:
            raise models.UserError("Les paramètres OpenBee pour la production ne sont pas configurés.")

        # Génération du PDF de l'ordre de fabrication
        report_name = 'ad_aero_report_p4.mrp_ordre_de_fabrication_report'
        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_name, [self.id])

        # Calcul du checksum SHA256
        checksum = hashlib.sha256(pdf_content).hexdigest()

        # Préparation des headers
        headers = {
            'OB-CHECKSUM': checksum,
            'OB-CHECKSUM-ALGO': 'sha256'
        }

        # Préparation des données du formulaire
        form_data = {
            'name': 'Ordre_Fabrication_' + str(self.id),
            'title': 'Ordre de Fabrication',
            'description': 'Ordre de fabrication' + str(self.name) + ' - ' + str(self.date_planned_start),
            # 'path': "/Ordre de fabrication/"+str(self.product_id.name),
            # 'idParentFolder': self.partner_id.openbee_folder_invoice_id,
            'type': params.type_id,  # ID de la catégorie "Factures" dans OpenBee
            'metadatas[11391]': self.product_id.name,
            'metadatas[11392]': self.bom_id.code,
            'metadatas[11393]': self.date_planned_start.strftime('%Y-%m-%d') if self.date_planned_start else '',
        }

        # Création d'un fichier temporaire pour stocker le PDF
        temp_handle, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
        try:
            with os.fdopen(temp_handle, 'wb') as pdf_file:
                pdf_file.write(pdf_content)

            with open(temp_pdf_path, 'rb') as pdf_file:
                files = {
                    'file': ('ordre_fabrication.pdf', pdf_file, 'application/pdf')
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
                    response_content = response.text  # Si la réponse n'est pas en JSON

                raise models.UserError(f'Message lors de l\'envoi vers OpenBee: {response_content}')

        finally:
            # Suppression du fichier temporaire
            try:
                os.unlink(temp_pdf_path)
            except Exception:
                pass
