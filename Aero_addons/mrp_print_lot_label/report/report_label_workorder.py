# -*- coding: utf-8 -*-

from odoo import api, models

class report_product_lot(models.AbstractModel):
    _name = 'report.mrp_print_lot_label.template_report_lot_label_workorder'

    @api.model
    def _get_report_values(self, docids, data=None):
        doc_ids = docids
        doc_model = self._context.get('active_model', 'mrp.production')

        docargs = {
            'doc_ids': doc_ids,
            'doc_model':  doc_model,
            'docs': self.env[doc_model].browse(doc_ids),
            'data': data,
        }
        return docargs