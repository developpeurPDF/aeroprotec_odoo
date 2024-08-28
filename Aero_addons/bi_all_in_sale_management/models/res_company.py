from odoo import fields, models, api, _

class InheritCompany(models.Model):
    _inherit="res.company"

    sale_color=fields.Char(string='Sale Color Code')
   