import base64
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class OpenBeeConnector(models.Model):
    _name = 'openbee.connector'
    _description = 'OpenBee Connector'

    document_id = fields.Char(string="Document ID")
    name = fields.Char(string="Document Name")
    client_name = fields.Char(string="Client Name")
    document_type = fields.Char(string="Document Type")
    amount_ht = fields.Float(string="Amount HT")
    amount_tva = fields.Float(string="Amount TVA")
    total_ttc = fields.Float(string="Total TTC")
    currency = fields.Char(string="Currency")
    status = fields.Char(string="Status")
    document_path = fields.Char(string="Document Path")
    file_uri = fields.Char(string="File URI")
    document_pdf = fields.Binary(string="PDF Document", attachment=True)
    document_name = fields.Char(string="PDF Name")
    document_url = fields.Char(string="Document URL")

    @api.model
    def fetch_openbee_data(self, document_id):
        url = f"https://actiondigitale.openbeedemo.com/ws/v2/document/{self.document_id}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        auth = ('florence@actiondigitale.net', '0penBee*2024')

        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            data = response.json()
            document = data.get('document', {})
            metadatas = {m['metadata']['name']: m['metadata']['value'] for m in data.get('metadatas', [])}
            # Télécharger le PDF depuis l'URL fileUri
            file_uri = document.get('fileUri')
            pdf_content = None
            if file_uri:
                pdf_response = requests.get(file_uri, auth=auth)
                if pdf_response.status_code == 200:
                    # Convertir le contenu du PDF en base64
                    pdf_content = base64.b64encode(pdf_response.content).decode('utf-8')

            # Créer ou mettre à jour l'enregistrement dans Odoo
            self.create({
                'document_id': document.get('idDocument'),
                'name': document.get('name'),
                'client_name': metadatas.get('Nom du client'),
                'document_type': metadatas.get('Type de document'),
                'amount_ht': float(metadatas.get('Montant(s) HT', 0)),
                'amount_tva': float(metadatas.get('Montant(s) TVA', 0)),
                'total_ttc': float(metadatas.get('Total TTC', 0)),
                'currency': metadatas.get('Devise'),
                'status': metadatas.get('Statut'),
                'document_path': document.get('path'),
                'file_uri': document.get('fileUri'),
                'document_pdf': pdf_content,
                'document_name': f"{document.get('name', 'document')}.pdf",
            })
        else:
            raise Exception(f"Failed to fetch data from OpenBee: {response.text}")



    def download_and_send_document(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        document_url = f"http://localhost:8090/report/pdf/account.report_invoice/{self.document_id}?db={self.env.cr.dbname}"
        login_url = f"http://localhost:8090/web/login?db={self.env.cr.dbname}"

        login_data = {
            "login": "c.devos@aeroprotec.com",
            "password": "@cU79pEt9E7!h?",  # À sécuriser
        }

        print(f"Document ID : {self.document_id}")
        print(f"Nom de la base de données : {self.env.cr.dbname}")

        session = requests.Session()

        try:
            # Connexion à Odoo
            login_response = session.post(login_url, data=login_data, allow_redirects=True)

            # Vérification de la réponse de la connexion
            if login_response.status_code != 200:
                raise UserError(f"Échec de connexion : {login_response.status_code} - {login_response.text}")

            # Vérification de la session
            if not session.cookies:
                raise UserError("Échec de la gestion des cookies. La session n'a pas été correctement établie.")

            print(f"Cookies après connexion : {session.cookies}")

            # Vérifier si l'URL existe
            print(f"URL du document: {document_url}")

            # Télécharger le PDF
            pdf_response = session.get(document_url, cookies=session.cookies)

            if pdf_response.status_code != 200:
                raise UserError(f"Erreur téléchargement PDF : {pdf_response.status_code} - {pdf_response.text}")

            file_data = pdf_response.content  # Contenu du fichier PDF

            # Envoi à OpenBee
            openbee_url = "https://actiondigitale.openbeedemo.com/ws/v2/queue"
            openbee_auth = ('florence@actiondigitale.net', '0penBee*2024')

            files = {'file': ('invoice.pdf', file_data, 'application/pdf')}
            response = requests.post(openbee_url, auth=openbee_auth, files=files)

            if response.status_code == 200:
                result = response.json()
                document_id = result.get('queueDocument', {}).get('id')

                if document_id:
                    # Classifier le document
                    classify_url = f"https://actiondigitale.openbeedemo.com/ws/v2/queue/{document_id}/classify"
                    folder_id = 52  # Assure-toi que cet ID est correct et défini
                    data = {'idFolder': folder_id}
                    classify_response = requests.post(classify_url, auth=openbee_auth, data=data)

                    if classify_response.status_code == 201:
                        self.document_url = f"https://actiondigitale.openbeedemo.com/ws/v2/queue/{document_id}/file"
                        print(f"Document envoyé et classifié. URL: {self.document_url}")
                    else:
                        raise UserError(
                            f"Erreur classification : {classify_response.status_code} - {classify_response.text}")
                else:
                    raise UserError(
                        f"Erreur récupération de l'ID du document : {response.status_code} - {response.text}")
            else:
                raise UserError(f"Erreur envoi OpenBee : {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise UserError(f"Erreur connexion : {e}")

    # def post_document_to_openbee(self):
    #     # URL de l'API OpenBee
    #     openbee_url = "https://actiondigitale.openbeedemo.com/ws/v2/document/upload"
    #
    #     # Authentification OpenBee
    #     openbee_auth = ('florence@actiondigitale.net', '0penBee*2024')
    #
    #     # URL du document à télécharger depuis Odoo
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     print("base_url", base_url)
    #     document_url = f"{base_url}/report/pdf/account.report_invoice/{self.document_id}"
    #     print("document_url", document_url)
    #
    #     try:
    #         # Créer une session pour gérer les cookies
    #
    #         login_url = f"{base_url}/web/login"
    #         print("login_url",login_url)
    #         login_data = {
    #             "login": self.env.user.login, # self.env.user.login "c.devos@aeroprotec.com"
    #             "password": "@cU79pEt9E7!h?",  # self.env.user.password "@cU79pEt9E7!h?" Assurez-vous que les identifiants sont corrects
    #             "db": self.env.cr.dbname,
    #         }
    #         print("login_data", login_data)
    #
    #         # Authentification à Odoo
    #         session = requests.Session()
    #         login_response = session.post(login_url, data=login_data)
    #         print("login_response", login_response.status_code)
    #         print("session.cookies", session.cookies)
    #
    #         # Vérifiez la réponse et la base de données sélectionnée
    #         _logger.info(f"Réponse de connexion : {login_response.status_code}")
    #         _logger.info(f"Cookies de la session : {session.cookies}")
    #
    #         if login_response.status_code != 200 or "session_id" not in session.cookies:
    #             raise UserError("Échec de la connexion à Odoo. Vérifiez les identifiants.")
    #         else:
    #             _logger.info("Connexion réussie à Odoo.")
    #
    #         # Vérifiez si la base de données est bien sélectionnée
    #         db_check_url = f"{base_url}/web/database/selector"
    #         db_check_response = session.get(db_check_url)
    #         if "Aero9" not in db_check_response.text:
    #             raise UserError("La base de données 'Aero9' n'est pas accessible.")
    #
    #         # Télécharger le document PDF
    #         response = session.get(document_url, timeout=30)
    #         response.raise_for_status()
    #
    #         # Vérifier si le fichier est un PDF
    #         if response.headers.get('Content-Type') != 'application/pdf':
    #             raise UserError("Le document téléchargé n'est pas un fichier PDF.")
    #     except requests.exceptions.RequestException as e:
    #         _logger.error(f"Erreur lors du téléchargement du document : {e}")
    #         raise UserError(f"Erreur lors du téléchargement du document : {e}")
    #
    #     # Préparer les métadonnées pour OpenBee
    #     metadata = {
    #         'name': self.document_name or f"Document_{self.id}",
    #         'type': self.document_type or 'Undefined Type',
    #         'client': self.client_name or 'Unknown Client',
    #     }
    #
    #     # Préparer le fichier à envoyer
    #     files = {
    #         'file': (f"{self.document_name or 'document'}.pdf", response.content, 'application/pdf'),
    #     }
    #
    #     try:
    #         # Envoyer le fichier à OpenBee
    #         openbee_response = requests.post(openbee_url, auth=openbee_auth, data=metadata, files=files, timeout=30)
    #         openbee_response.raise_for_status()
    #     except requests.exceptions.RequestException as e:
    #         _logger.error(f"Erreur lors de l'envoi à OpenBee : {e}")
    #         raise UserError(f"Erreur lors de l'envoi à OpenBee : {e}")
    #
    #     # Vérifier la réponse de l'API OpenBee
    #     if openbee_response.status_code == 200:
    #         try:
    #             result = openbee_response.json()
    #             self.message_post(body=f"Document envoyé avec succès à OpenBee : {result}")
    #         except ValueError:
    #             raise UserError("Le serveur OpenBee a retourné une réponse invalide.")
    #     else:
    #         _logger.error(f"Erreur OpenBee : {openbee_response.status_code}, {openbee_response.text}")
    #         raise UserError(f"Erreur OpenBee : {openbee_response.status_code}, {openbee_response.text}")







    # def _get_openbee_credentials(self):
    #     """Get OpenBee credentials from system parameters."""
    #     return {
    #         'username': 'florence@actiondigitale.net',
    #         'password': '0penBee*2024',
    #         'base_url': 'https://actiondigitale.openbeedemo.com',
    #     }
    #
    # def _get_odoo_credentials(self):
    #     """Get Odoo credentials from system parameters."""
    #     return {
    #         'login': 'c.devos@aeroprotec.com',  # Notez le changement de 'username' à 'login'
    #         'password': '@cU79pEt9E7!h?',
    #     }
    #
    # def _get_pdf_document(self, session):
    #     """Download PDF document from Odoo."""
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     document_url = f"{base_url}/report/pdf/account.report_invoice/{self.document_id}?db={self.env.cr.dbname}"
    #
    #     print("Downloading PDF from: %s", document_url)
    #     response = session.get(document_url, cookies=session.cookies)
    #
    #     if response.status_code != 200:
    #         raise UserError(_("Failed to download PDF: %s") % response.text)
    #
    #     return response.content
    #
    # def _send_to_openbee(self, file_data):
    #     """Send document to OpenBee."""
    #     credentials = self._get_openbee_credentials()
    #     openbee_url = f"{credentials['base_url']}/ws/v2/queue"
    #
    #     files = {'file': ('invoice.pdf', file_data, 'application/pdf')}
    #     auth = (credentials['username'], credentials['password'])
    #
    #     print("Sending document to OpenBee")
    #     response = requests.post(openbee_url, auth=auth, files=files)
    #
    #     if response.status_code != 200:
    #         raise UserError(_("Failed to send to OpenBee: %s") % response.text)
    #
    #     return response.json()
    #
    # def _classify_document(self, document_id):
    #     """Classify document in OpenBee."""
    #     credentials = self._get_openbee_credentials()
    #     classify_url = f"{credentials['base_url']}/ws/v2/queue/{document_id}/classify"
    #
    #     data = {'idFolder': 52}  # Consider making folder ID configurable
    #     auth = (credentials['username'], credentials['password'])
    #
    #     print("Classifying document in OpenBee")
    #     response = requests.post(classify_url, auth=auth, json=data)
    #
    #     if response.status_code != 201:
    #         raise UserError(_("Failed to classify document: %s") % response.text)
    #
    #     return response.json()
    #
    # def download_and_send_document(self):
    #     """Main method to download and send document to OpenBee."""
    #     try:
    #         # Initialize session
    #         session = requests.Session()
    #
    #         # Get Odoo credentials and login
    #         credentials = self._get_odoo_credentials()
    #         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         login_url = f"{base_url}/web/login"
    #
    #         print("Logging into Odoo")
    #         login_response = session.post(login_url, data=credentials)
    #
    #         if login_response.status_code != 200:
    #             raise UserError(_("Failed to login to Odoo"))
    #
    #         # Download PDF
    #         file_data = self._get_pdf_document(session)
    #
    #         # Send to OpenBee
    #         result = self._send_to_openbee(file_data)
    #         document_id = result.get('queueDocument', {}).get('id')
    #
    #         if not document_id:
    #             raise UserError(_("Failed to get document ID from OpenBee"))
    #
    #         # Classify document
    #         self._classify_document(document_id)
    #
    #         # Update document URL
    #         credentials = self._get_openbee_credentials()
    #         self.document_url = f"{credentials['base_url']}/ws/v2/queue/{document_id}/file"
    #
    #         print("Document successfully sent and classified in OpenBee")
    #         return True
    #
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Connection error: %s", str(e))
    #         raise UserError(_("Connection error: %s") % str(e))
    #     except Exception as e:
    #         _logger.error("Unexpected error: %s", str(e))
    #         raise UserError(_("Unexpected error: %s") % str(e))


    def post_document_to_openbee(self):
        # Charger le fichier statique
        file_path = 'C:/Users/DELL/Desktop/WS odoo16CE/server/Aero_addons/ad_openbee_api/static/description/1.pdf'

        # Ouvrir et lire le fichier PDF en mode binaire
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
        except Exception as e:
            raise UserError(f"Erreur lors de la lecture du fichier PDF : {e}")

        # URL de l'API OpenBee pour ajouter un fichier dans la file d'attente
        openbee_url = "https://actiondigitale.openbeedemo.com/ws/v2/queue"

        # Authentification OpenBee
        openbee_auth = ('florence@actiondigitale.net', '0penBee*2024')

        # Préparer les données à envoyer dans la requête
        files = {
            'file': ('1.pdf', file_data, 'application/pdf')
        }

        try:
            # Effectuer la requête POST pour envoyer le document à OpenBee
            response = requests.post(openbee_url, auth=openbee_auth, files=files)

            # Vérifier la réponse
            if response.status_code == 200:
                result = response.json()
                # Extraire l'ID du document de la réponse
                document_id = result.get('queueDocument', {}).get('id')

                # URL pour classifier le document dans un dossier spécifique
                classify_url = f"https://actiondigitale.openbeedemo.com/ws/v2/queue/{document_id}/classify"

                # ID du dossier où vous souhaitez déplacer le document
                folder_id = 52  # ID du dossier cible

                # Préparer les données de classification
                data = {
                    'idFolder': folder_id,
                }

                # Effectuer la requête POST pour classifier le document
                classify_response = requests.post(classify_url, auth=openbee_auth, data=data)

                if classify_response.status_code == 201:
                    # Document classifié avec succès
                    self.document_url = f"https://actiondigitale.openbeedemo.com/ws/v2/queue/{document_id}/file"
                    _logger.info(
                        f"Document envoyé et classifié avec succès dans le dossier {folder_id}. URL: {self.document_url}")
                else:
                    _logger.error(
                        f"Erreur lors de la classification du document: {classify_response.status_code} - {classify_response.text}")
                    raise UserError(
                        f"Erreur lors de la classification du document: {classify_response.status_code} - {classify_response.text}")

            else:
                _logger.error(f"Erreur lors de l'envoi du document: {response.status_code} - {response.text}")
                raise UserError(f"Erreur lors de l'envoi du document: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur de connexion à OpenBee: {e}")
            raise UserError(f"Erreur de connexion à OpenBee: {e}")