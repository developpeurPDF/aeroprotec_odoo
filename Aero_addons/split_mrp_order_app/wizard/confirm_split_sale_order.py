# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SplitManufacturing(models.TransientModel):	
	_name = "split.mo.order"
	_description = "Split Manufacturing"

	spliting_method = fields.Selection([('by_qty', 'By Number of Quantity'), ('by_split', 'By Number of Split')],string = 'Spliting Method', required=True)
	no_qty = fields.Integer("Number of Quantity")
	no_split = fields.Integer("Number of Split")

	# split Manufacturing using number of qty and number of split mo
	def split_confirm(self):
		current_id = self._context.get('active_id')
		mo_order = self.env['mrp.production'].browse(current_id)

		if self.spliting_method == 'by_split':
			if self.no_split <= 0:
				raise ValidationError(_('Please enter data for split number of Manufacturing Orders..!')) 

			divide_qty = mo_order.product_qty/self.no_split
			mo_order.write({'product_qty':divide_qty})
			no_split = self.no_split-1

			for i in range(0,no_split):
				qty_list = []
				for line in mo_order.move_raw_ids:
					stock_move = self.env['stock.move'].create(
						{'product_id':line.product_id.id,
						'location_id':line.location_id.id,
						'location_dest_id':line.location_dest_id.id,
						'name':line.name,
						'is_split_mo':True,
						'lot_ids':line.lot_ids,
						'product_uom_qty':line.product_uom_qty/self.no_split,
						'product_uom':line.product_uom.id})
					qty_list.append(stock_move.id)

				new_mo_order = mo_order.copy()

				new_mo_order.update({'origin':mo_order.origin,
					'product_qty':divide_qty,
					'is_split_mo':True,
					'move_raw_ids':[(6,0,qty_list)],
					})

			for line in mo_order.move_raw_ids:
				line.update({'product_uom_qty':line.product_uom_qty/self.no_split})

		if self.spliting_method == 'by_qty':
			if self.no_qty <= 0:
				raise ValidationError(_('Please enter valid Number of Quantity...!'))
			if self.no_qty > mo_order.product_qty:
				raise ValidationError(_('Please enter smaller qty than current MO Qty...!'))

			qty_list = []
			for line in mo_order.move_raw_ids:
				div_mo_qty = line.product_uom_qty/mo_order.product_qty
				stock_move = self.env['stock.move'].create(
					{'product_id':line.product_id.id,
					'name':line.name,
					'is_split_mo':True,
					'location_id':line.location_id.id,
					'location_dest_id':line.location_dest_id.id,
					'lot_ids':line.lot_ids,
					'product_uom_qty':div_mo_qty * self.no_qty,
					'product_uom':line.product_uom.id,
					})
				qty_list.append(stock_move.id)

			new_mo = mo_order.copy()
			new_mo.update({'origin':mo_order.origin,
				'product_qty':self.no_qty,
				'is_split_mo':True,
				'move_raw_ids':[(6,0,qty_list)],
				})

			for line in mo_order.move_raw_ids:
				div_qty = line.product_uom_qty/mo_order.product_qty
				min_line_qty = (div_qty * self.no_qty)
				line.update({'product_uom_qty':line.product_uom_qty - min_line_qty})
			mo_order.update({'product_qty':mo_order.product_qty - self.no_qty})


class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	is_split_mo = fields.Boolean()

	def write(self,vals):
		res = super(MrpProduction,self).write(vals)
		if self.is_split_mo:
			if 'product_id' in vals or 'product_qty' in vals or 'bom_id' in vals:
				if self.move_raw_ids:
					for move in self.move_raw_ids:
						if move.is_split_mo and move.state=='draft':
							move.unlink()
		return res


class StockMove(models.Model):
	_inherit = 'stock.move'

	is_split_mo = fields.Boolean()

