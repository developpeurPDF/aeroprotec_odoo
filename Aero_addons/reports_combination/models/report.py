# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode
from io import BytesIO
from logging import getLogger
import PyPDF2

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas

from PIL import Image

from odoo import api, fields, models, tools

from odoo.exceptions import ValidationError

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass

logger = getLogger(__name__)

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    logger.debug("Can not import PyPDF2")


class Report(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if not self.env.context.get("res_ids"):
            return super(Report, self.with_context(res_ids=res_ids))._render_qweb_pdf(report_ref=report_ref,
                                                                                      res_ids=res_ids, data=data)
        return super(Report, self)._render_qweb_pdf(report_ref=report_ref, res_ids=res_ids, data=data)

    # @api.model
    # def _run_wkhtmltopdf(
    #         self,
    #         bodies,
    #         report_ref=False,
    #         header=None,
    #         footer=None,
    #         landscape=False,
    #         specific_paperformat_args=None,
    #         set_viewport_size=False):
    #     result = super(Report, self)._run_wkhtmltopdf(bodies, header=header, report_ref=report_ref, footer=footer,
    #                                                   landscape=landscape,
    #                                                   specific_paperformat_args=specific_paperformat_args,
    #                                                   set_viewport_size=set_viewport_size,
    #                                                   )
    #     if report_ref != 'reports_combination.report_saleorder_cgv':
    #         return result
    #     pdf = PdfFileWriter()
    #     pdf_watermark = None
    #     watermark = None
    #     docids = self.env.context.get("res_ids", False)
    #     sale_id = self.env['sale.order'].browse(docids)
    #     if sale_id and sale_id.file_terms:
    #         watermark = b64decode(sale_id.file_terms)
    #
    #     speech_watermark = None  # Initialize speech_watermark
    #     if sale_id and sale_id.company_id.agence_id and sale_id.company_id.pdf_model == 'best_termites' and sale_id.speech_pdf:
    #         speech_watermark = b64decode(sale_id.speech_pdf)
    #
    #     if not watermark:
    #         logger.info("pas watermark")
    #         return result
    #     try:
    #         pdf_watermark = PdfFileReader(BytesIO(watermark), strict=False, overwriteWarnings=False)
    #     except PdfReadError as e:
    #         logger.exception("Failed to load watermark", e)
    #         return result
    #
    #     if not pdf_watermark:
    #         logger.error("No usable watermark found, got %s...", watermark[:100])
    #         return result
    #
    #     if pdf_watermark.numPages < 1:
    #         logger.error("Your watermark pdf does not contain any pages")
    #         return result
    #     reader = PdfFileReader(BytesIO(result), strict=False, overwriteWarnings=False)
    #
    #     for page in reader.pages:
    #         print(pdf_watermark.numPages)
    #
    #         pdf.addPage(page)
    #
    #     for page in pdf_watermark.pages:
    #         pdf.addPage(page)
    #
    #     if speech_watermark:
    #         try:
    #             speech_pdf = PdfFileReader(BytesIO(speech_watermark), strict=False, overwriteWarnings=False)
    #             for page in speech_pdf.pages:
    #                 pdf.addPage(page)
    #         except PdfReadError as e:
    #             logger.exception("Failed to load speech pdf", e)
    #
    #     pdf_content = BytesIO()
    #     pdf.write(pdf_content)
    #
    #     return pdf_content.getvalue()

    # @api.model
    # def _run_wkhtmltopdf(
    #         self,
    #         bodies,
    #         report_ref=False,
    #         header=None,
    #         footer=None,
    #         landscape=False,
    #         specific_paperformat_args=None,
    #         set_viewport_size=False):
    #     result = super(Report, self)._run_wkhtmltopdf(bodies, header=header, report_ref=report_ref, footer=footer,
    #                                                   landscape=landscape,
    #                                                   specific_paperformat_args=specific_paperformat_args,
    #                                                   set_viewport_size=set_viewport_size,
    #                                                   )
    #     if report_ref != 'reports_combination.report_saleorder_cgv':
    #         return result
    #
    #     pdf = PdfFileWriter()
    #     pdf_watermark = None
    #     watermark = None
    #     docids = self.env.context.get("res_ids", False)
    #     sale_id = self.env['sale.order'].browse(docids)
    #     if sale_id and sale_id.file_terms:
    #         watermark = b64decode(sale_id.file_terms)
    #
    #     speech_watermark = None
    #     if sale_id and sale_id.company_id.agence_id and sale_id.company_id.pdf_model == 'best_termites' and sale_id.speech_pdf:
    #         speech_watermark = b64decode(sale_id.speech_pdf)
    #
    #     if not watermark:
    #         logger.info("pas watermark")
    #         return result
    #
    #     try:
    #         pdf_watermark = PdfFileReader(BytesIO(watermark), strict=False, overwriteWarnings=False)
    #     except PdfReadError as e:
    #         logger.exception("Failed to load watermark", e)
    #         return result
    #
    #     if not pdf_watermark:
    #         logger.error("No usable watermark found, got %s...", watermark[:100])
    #         return result
    #
    #     if pdf_watermark.numPages < 1:
    #         logger.error("Your watermark pdf does not contain any pages")
    #         return result
    #
    #     reader = PdfFileReader(BytesIO(result), strict=False, overwriteWarnings=False)
    #
    #     for page in reader.pages:
    #         pdf.addPage(page)
    #
    #     for i, page in enumerate(pdf_watermark.pages):
    #         if i == 0:
    #             # Add the first page of the watermark
    #             pdf.addPage(page)
    #
    #             # Add speech_pdf content after the first page
    #             if speech_watermark:
    #                 try:
    #                     speech_pdf = PdfFileReader(BytesIO(speech_watermark), strict=False, overwriteWarnings=False)
    #                     for speech_page in speech_pdf.pages:
    #                         pdf.addPage(speech_page)
    #                 except PdfReadError as e:
    #                     logger.exception("Failed to load speech pdf", e)
    #         else:
    #             # Add remaining pages of the watermark as well as the rest of the CGV pages
    #             pdf.addPage(page)
    #
    #     pdf_content = BytesIO()
    #     pdf.write(pdf_content)
    #
    #     return pdf_content.getvalue()

    @api.model
    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        result = super(Report, self)._run_wkhtmltopdf(bodies, header=header, report_ref=report_ref, footer=footer,
                                                      landscape=landscape,
                                                      specific_paperformat_args=specific_paperformat_args,
                                                      set_viewport_size=set_viewport_size,
                                                      )
        if report_ref != 'reports_combination.report_saleorder_cgv':
            return result

        pdf = PdfFileWriter()
        pdf_watermark = None
        watermark = None
        docids = self.env.context.get("res_ids", False)
        sale_id = self.env['sale.order'].browse(docids)
        if sale_id and sale_id.file_terms:
            watermark = b64decode(sale_id.file_terms)

        speech_watermark = None
        # if sale_id.speech_pdf:
        #     speech_watermark = b64decode(sale_id.speech_pdf)

        if not watermark:
            logger.info("pas watermark")
            return result

        try:
            pdf_watermark = PdfFileReader(BytesIO(watermark), strict=False, overwriteWarnings=False)
        except PdfReadError as e:
            logger.exception("Failed to load watermark", e)
            return result

        if not pdf_watermark:
            logger.error("No usable watermark found, got %s...", watermark[:100])
            return result

        if pdf_watermark.numPages < 1:
            logger.error("Your watermark pdf does not contain any pages")
            return result

        reader = PdfFileReader(BytesIO(result), strict=False, overwriteWarnings=False)

        # Add the first page from the original result
        pdf.addPage(reader.getPage(0))

        # Add the pages from the speech_watermark after the first page
        if speech_watermark:
            try:
                speech_pdf = PdfFileReader(BytesIO(speech_watermark), strict=False, overwriteWarnings=False)
                for speech_page in speech_pdf.pages:
                    pdf.addPage(speech_page)
            except PdfReadError as e:
                logger.exception("Failed to load speech pdf", e)

        # Add the remaining pages from the original result
        for i in range(1, reader.getNumPages()):
            pdf.addPage(reader.getPage(i))

        # Add the pages from the watermark at the end
        for i in range(pdf_watermark.getNumPages()):
            pdf.addPage(pdf_watermark.getPage(i))

        pdf_content = BytesIO()
        pdf.write(pdf_content)

        return pdf_content.getvalue()




















