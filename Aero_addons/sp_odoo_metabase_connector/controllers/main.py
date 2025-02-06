from odoo import http, _
from odoo.http import request


class MainController(http.Controller):

    @http.route(['/check/menu/dashboard'], type='json', auth='user')
    def validate_menu_dashboard(self, menu_id):
        """ it is return iframe url """
        if menu_id:
            menu = request.env['dashboard.menu'].sudo().search([('menu_id', '=', int(menu_id))], limit=1)
            if menu and menu.is_add_dashboard and menu.dashboard_iframe_src:
                return menu.dashboard_iframe_src
        return False
