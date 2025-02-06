from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MetabaseDashboard(models.Model):
    _name = 'metabase.dashboard'
    _description = 'available metabase dashboard'

    name = fields.Char('Metabase Dashboard Name', required=True)
    origin_id = fields.Char('Origin')
    public_uuid = fields.Char('Metabase Dashboard Public UUID')
    configuration_id = fields.Many2one('metabase.configuration', 'Configuration')
    menu_line = fields.One2many('dashboard.menu', 'dashboard_id', 'Menu')

    def action_open_dashboard_form_view(self):
        return {
            'name': 'Dashboard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'res_model': 'metabase.dashboard',
        }

    def unlink(self):
        """ unlink all dashboard -> menu -> action """
        dashboard_menu_records = self.mapped('menu_line')
        if dashboard_menu_records:
            menu_ids = dashboard_menu_records.mapped('menu_id')
            for menu in menu_ids:
                if menu and menu.action:
                    menu.action.sudo().unlink()
            menu_ids.sudo().unlink()
        return super(MetabaseDashboard, self).unlink()

    @api.constrains('menu_line', 'menu_line.groups_id')
    def add_access_group_to_menu(self):
        if self.menu_line:
            for line in self.menu_line:
                line.menu_id.groups_id = False
                if line.groups_id:
                    line.menu_id.write({
                        'groups_id': [(4, group.id) for group in line.groups_id]
                    })


class DashboardMenu(models.Model):
    _name = 'dashboard.menu'
    _description = 'Dashboard menu'

    name = fields.Char('Name', required=True)
    is_add_dashboard = fields.Boolean('Is Add Dashboard', default=False)
    sequence = fields.Integer('Sequence', default=10, required=True)
    menu_id = fields.Many2one('ir.ui.menu', 'Menu')
    parent_menu_id = fields.Many2one('ir.ui.menu', 'Parent Menu', required=True)
    dashboard_iframe_src = fields.Char('IframeSrc')
    dashboard_id = fields.Many2one('metabase.dashboard', 'Dashboard')
    groups_id = fields.Many2many('res.groups', 'ir_ui_menu_group_dashboard_rel',
                                 'dashboard_menu_id', 'menu_id', string='Access Groups',
                                 help="If you have groups, the visibility of this menu will be based on these groups. ")

    def generate_iframe(self, dashboard_id):
        """ return: generated iframe src """
        if dashboard_id:
            dashboard_id = self.env['metabase.dashboard'].browse(dashboard_id)
            config = self.env['metabase.configuration'].sudo().search([], limit=1)
            dashboard_iframe_src = f"{config.ip}/public/dashboard/{dashboard_id.public_uuid}"
            return dashboard_iframe_src

    def create_dashboard_menu(self, vals):
        """ create menu for add metabase dashboard """
        menu_id = self.env['ir.ui.menu'].sudo().create({
            'name': vals.get('name'),
            'sequence': vals.get('sequence'),
            'parent_id': vals.get('parent_menu_id'),
        })
        return menu_id

    def create_action(self, res, menu_id):
        """ Create an action for the dashboard menu """
        return self.env['ir.actions.client'].sudo().create({
            'name': res.name,
            'tag': 'sp_odoo_metabase_connector.attached_dashboard_view',
            'params': {'_id': menu_id.id}
        })

    @api.model
    def create(self, vals):
        menu_id = self.create_dashboard_menu(vals)
        dashboard_id = vals.get('dashboard_id')
        if not dashboard_id:
            raise ValidationError(_('Dashboard not found.'))
        url = self.generate_iframe(vals.get('dashboard_id'))
        res = super(DashboardMenu, self).create(vals)
        if menu_id and url:
            res.menu_id = menu_id.id
            res.dashboard_iframe_src = url
            action = self.create_action(res, menu_id)
            menu_id.action = f'ir.actions.client,{action.id}'
            res.is_add_dashboard = True
        return res

    def unlink(self):
        """ unlink all menu and action """
        menu_ids = self.mapped('menu_id')
        if menu_ids:
            for menu in menu_ids:
                if menu and menu.action:
                    menu.action.sudo().unlink()
            menu_ids.sudo().unlink()
        return super(DashboardMenu, self).unlink()
