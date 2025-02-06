from odoo import fields, models, api, _
import requests
from odoo.exceptions import ValidationError


# =========================================
#  Metabase configuration
# =========================================

class MetabaseConfiguration(models.Model):
    _name = 'metabase.configuration'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    ip = fields.Char('URL', required=True)
    api_key = fields.Char('Api Key', required=True)
    dashboard_line = fields.One2many('metabase.dashboard', 'configuration_id', 'Dashboard')

    @api.model
    def show_notification(self, msg, type):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': msg,
                'sticky': False,
                'type': type
            }
        }

    def get_api_response(self):
        if not self.ip:
            raise ValidationError(_('Please provide a URL.'))
        if not self.api_key:
            raise ValidationError(_('Please provide an API key.'))
        url = f"{self.ip}/api/dashboard/public"
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        response = requests.get(url, headers=headers)
        return response

    def check_metabase_connection(self):
        """ Check metabase connection """
        response = self.get_api_response()
        if response.status_code == 200:
            return self.show_notification('Connection success', 'success')
        else:
            return self.show_notification('Connection failed', 'danger')

    def create_dashboard(self, dashboards):
        """ create metabase dashboard """
        for dashboard in dashboards:
            already_exist = self.env['metabase.dashboard'].sudo().search(
                [('origin_id', '=', dashboard.get('id'))])
            if not already_exist:
                self.env['metabase.dashboard'].sudo().create({
                    'name': dashboard.get('name'),
                    'origin_id': dashboard.get('id'),
                    'public_uuid': dashboard.get('public_uuid'),
                    'configuration_id': self.id
                })

    def fetch_metabase_dashboard(self):
        """ fetch metabase dashboard """
        response = self.get_api_response()
        if response.status_code == 200:
            dashboards = response.json()
            self.create_dashboard(dashboards)
        else:
            error_message = response.text  # Capture the raw response text
            raise ValidationError(
                _("Failed to fetch dashboard. Status: %d, Response: %s") % (response.status_code, error_message))
