# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools



class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    file_terms = fields.Binary(related="sale_order_template_id.file_terms")