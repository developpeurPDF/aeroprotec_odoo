# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools
from base64 import b64decode
from io import BytesIO
from logging import getLogger
_logger = getLogger(__name__)
try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    _logger.debug("Can not import PyPDF2")



class SaleOrderTemplateInherit(models.Model):
    _inherit = "sale.order.template"

    file_terms = fields.Binary(string="File CGV", attachment=True)
    number_pages= fields.Integer("Number of pages",compute="get_number_of_pages",store=True)

    @api.depends("file_terms")
    def get_number_of_pages(self):
        for rec in self:
            if rec.file_terms:
                pdf_watermark = None
                watermark = None
                watermark = b64decode(rec.file_terms)
                try:
                    pdf_watermark = PdfFileReader(BytesIO(watermark), strict=False, overwriteWarnings=False)
                    rec.number_pages = pdf_watermark.numPages
                except PdfReadError as e:
                    rec.number_pages = 0