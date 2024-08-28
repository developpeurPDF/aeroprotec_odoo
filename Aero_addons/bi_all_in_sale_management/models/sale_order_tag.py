# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields,_


class CRMTagInherit(models.Model):
	_inherit = "crm.tag"

	view_ids = fields.Many2many('ir.ui.view',string="Views")
	compute_tag = fields.Char(string='Tag Compute',compute='_tag_comp')


	@api.model_create_multi
	def create(self,vals):
		res=super(CRMTagInherit,self).create(vals)
		quotation_id=self.env.ref('sale.sale_order_view_search_inherit_quotation')
		order_id=self.env.ref('sale.sale_order_view_search_inherit_sale')
		filter_name = 'filter_'+res.name

		arch_base=_("""<?xml version='1.0'?>\n
			<data>\n
			<xpath expr="//separator[3]" position="after">\n
			<filter string="%s" name="tag_%s" domain="[('tag_ids','ilike','%s')]"/>\n
			</xpath>\n
			</data>""") % (res.name,filter_name,res.name)

		order_arch_base=_("""<?xml version='1.0'?>\n
			<data>\n
			<xpath expr="//separator[2]" position="after">\n
			<filter string="%s" name="tag_%s" domain="[('tag_ids','ilike','%s')]"/>\n
			</xpath>\n
			</data>""") % (res.name,filter_name,res.name)
		
		quotation_vals = {
			'name': 'quotation.tag.filter.%s' % res.name,
			'type': 'search',
			'model': 'sale.order',
			'mode': 'extension',
			'inherit_id': quotation_id.id,
			'arch_base': arch_base,
			'active': True
		}
		
		order_vals = {
			'name': 'order.tag.filter.%s' % res.name,
			'type': 'search',
			'model': 'sale.order',
			'mode': 'extension',
			'inherit_id': order_id.id,
			'arch_base': order_arch_base,
			'active': True
		}
		
		quotation_view_id = self.env['ir.ui.view'].sudo().create(quotation_vals)
		order_view_id = self.env['ir.ui.view'].sudo().create(order_vals)
		

		res.write({'view_ids' : [(4,quotation_view_id.id)]})
		res.write({'view_ids' : [(4,order_view_id.id)]})
	
		
		return res

	def write(self,vals):
		res=super(CRMTagInherit,self).write(vals)
		quotation_id=self.env.ref('sale.sale_order_view_search_inherit_quotation')
		order_id=self.env.ref('sale.sale_order_view_search_inherit_sale')
		filter_name = 'filter_'+self.name
		arch_base=_("""<?xml version='1.0'?>\n
			<data>\n
			<xpath expr="//separator[3]" position="after">\n
			<filter string="%s" name="tag_%s" domain="[('tag_ids','ilike','%s')]"/>\n
			</xpath>\n
			</data>""") % (self.name,filter_name,self.name)

		order_arch_base=_("""<?xml version='1.0'?>\n
			<data>\n
			<xpath expr="//separator[2]" position="after">\n
			<filter string="%s" name="tag_%s" domain="[('tag_ids','ilike','%s')]"/>\n
			</xpath>\n
			</data>""") % (self.name,filter_name,self.name)

		for data in self.view_ids:
			if data['inherit_id']==quotation_id:
				data.write({'arch_base':arch_base})
			if data['inherit_id']==order_id:
				data.write({'arch_base':order_arch_base})

		return res

	def unlink(self):
		for rec in self:
			rec.view_ids.unlink()	
		return super(CRMTagInherit, self).unlink()
	
	
	def _tag_comp(self):
		tag_list=[]

		for record in self:
			record.compute_tag = None

			quotation_id=self.env.ref('sale.sale_order_view_search_inherit_quotation')
			order_id=self.env.ref('sale.sale_order_view_search_inherit_sale')
			filter_name = 'filter_'+record.name

			arch_base=_("""<?xml version='1.0'?>\n
				<data>\n
				<xpath expr="//separator[3]" position="after">\n
				<filter string="%s" name="tag_%s" domain="[('tag_ids','ilike','%s')]"/>\n
				</xpath>\n
				</data>""") % (record.name,filter_name,record.name)

			order_arch_base=_("""<?xml version='1.0'?>\n
				<data>\n
				<xpath expr="//separator[2]" position="after">\n
				<filter string="%s" name="tag_%s" domain="[('tag_ids','ilike','%s')]"/>\n
				</xpath>\n
				</data>""") % (record.name,filter_name,record.name)
			
			quotation_vals = {
				'name': 'quotation.tag.filter.%s' % record.name,
				'type': 'search',
				'model': 'sale.order',
				'mode': 'extension',
				'inherit_id': quotation_id.id,
				'arch_base': arch_base,
				'active': True
			}
			
			order_vals = {
				'name': 'order.tag.filter.%s' % record.name,
				'type': 'search',
				'model': 'sale.order',
				'mode': 'extension',
				'inherit_id': order_id.id,
				'arch_base': order_arch_base,
				'active': True
			}
			available_tag_quotation = self.env['ir.ui.view'].search([('name','=','quotation.tag.filter.%s' % record.name)])
			available_tag_order = self.env['ir.ui.view'].search([('name','=','quotation.tag.filter.%s' % record.name)])
			
			if not available_tag_quotation:
				quotation_view_id = self.env['ir.ui.view'].sudo().create(quotation_vals)
				record.write({'view_ids' : [(4,quotation_view_id.id)]})
			if not available_tag_order:
				order_view_id = self.env['ir.ui.view'].sudo().create(order_vals)			
				record.write({'view_ids' : [(4,order_view_id.id)]})

