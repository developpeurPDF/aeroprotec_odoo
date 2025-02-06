# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Robin K(<robin@cybrosys.info>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_line_image = fields.Binary(string="Image",
                                     related="product_id.image_1920")
    contact_email = fields.Char(related="order_partner_id.email")
    contact_phone = fields.Char(related="order_partner_id.phone")
    produce_delay = fields.Float(string="Durée du cycle")
    days_to_prepare_mo = fields.Float(string="Jours pour préparer l'ordre de fabrication")
    sale_delay = fields.Float(string="Durée du cycle négocié avec le client")

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        if self.product_template_id:
            self.produce_delay = self.product_template_id.produce_delay
            self.days_to_prepare_mo = self.product_template_id.days_to_prepare_mo
            self.sale_delay = self.product_template_id.sale_delay


    date_commande = fields.Datetime(string="Date de la commande", related="order_id.date_order")

