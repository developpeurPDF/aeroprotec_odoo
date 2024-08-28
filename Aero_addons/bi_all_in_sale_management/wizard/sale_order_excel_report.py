from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.tools.misc import xlwt
from PIL import Image ,ImageColor
from io import  BytesIO
from webcolors import hex_to_rgb ,rgb_to_hex
import webcolors
import io
import base64



class SaleOrderReportWiz(models.TransientModel):
    _name = 'sale.order.report.wiz'
    _description = 'Sale Order Report Wizard'

    def get_resized_image_data(self, file_path, bound_width_height):
        # get the image and resize it
        im = Image.open(file_path)
        im.thumbnail(bound_width_height, Image.ANTIALIAS)  # ANTIALIAS is important if shrinking

        # stuff the image data into a bytestream that excel can read
        im_bytes = BytesIO()
        im.save(im_bytes, format='PNG')
        return im_bytes


    def print_sale_order_report(self):

        filename = 'Quotation/Sale Order Report' + '.xls'
        order_data = self.env['sale.order'].sudo().browse(self._context.get('active_id'))       

        for rec in order_data:
            if rec.company_id.sale_color:
                def closest_colour(requested_colour):
                    min_colours = {}
                    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
                        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
                        rd = (r_c - requested_colour[0]) ** 2
                        gd = (g_c - requested_colour[1]) ** 2
                        bd = (b_c - requested_colour[2]) ** 2
                        min_colours[(rd + gd + bd)] = name
                    return min_colours[min(min_colours.keys())]

                def get_colour_name(requested_colour):
                    try:
                        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
                    except ValueError:
                        closest_name = closest_colour(requested_colour)
                        actual_name = None
                    return actual_name, closest_name
                hextorgb=ImageColor.getcolor(rec.company_id.sale_color,"RGB")
                rgb_code=hextorgb
                # rgbstr=rgb_code[1:-1]
                # rgblist=rgb_code.split(',')
                rgblist=list(map(int,rgb_code))
                requested_colour = rgblist
                actual_name, closest_name = get_colour_name(requested_colour)
                xlwt.add_palette_colour("{}".format(closest_name) ,0x21)

            workbook = xlwt.Workbook()
            if rec.company_id.sale_color: 
                workbook.set_colour_RGB(0x21, requested_colour[0],requested_colour[1],requested_colour[2]) # 0xF1D9C5 in excel palette location 0x21
            

            worksheet = workbook.add_sheet('Quotation/Sale Order Report')
            font = xlwt.Font()
            font.bold = True
            color_code=''
            if rec.company_id.sale_color:
                color_code=closest_name
            else:
                color_code='black'
            
            for_left_not_bold = xlwt.easyxf("font: name Arial,color black; align: horiz center")
            number_format = xlwt.easyxf("font: name Arial,color black; align: horiz center",num_format_str='0.00')
            color_blue = xlwt.easyxf("font: bold True,name Arial, color white; align: horiz center;pattern: pattern solid, fore_color {}".format(color_code))
            blue_text = xlwt.easyxf("font: name Arial,color {}; align: horiz center;".format(color_code))
            Thank_size = xlwt.easyxf("font: bold True,name Arial,height 320, color {}; align: horiz center;".format(color_code))
            
            bill_title = xlwt.easyxf(
                'font: bold True,color {}, name Arial, height 350;'
                'align:horizontal right, wrap on;'
                'borders: top medium, bottom medium, left medium, right medium;'.format(color_code)
            )
            style = xlwt.easyxf(
                'font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
        
            alignment = xlwt.Alignment()  # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_RIGHT
            style = xlwt.easyxf('align: wrap yes')
            style.num_format_str = '0.00'

            worksheet.row(0).height = 1200
            worksheet.col(0).width = 15000
            worksheet.col(1).width = 1000
            worksheet.col(2).width = 3000
            worksheet.col(3).width = 4000
            worksheet.col(4).width = 4000

            buf_image = BytesIO(base64.b64decode(rec.company_id.logo))

            bound_width_height = (270, 140)


            image_data = self.get_resized_image_data(buf_image, bound_width_height)

            
            img = Image.open(image_data).convert("RGB")
            
            fo = BytesIO()
            img.save(fo, format='bmp')
            worksheet.insert_bitmap_data(fo.getvalue(),0,0,0,0,1,0.14)
            workbook.save('filename.xls')
            img.close()
            if rec.state =="draft":
                worksheet.write_merge(
                    0, 0, 3, 4, 'QUOTATION', bill_title)
            if rec.state =="sent":
                worksheet.write_merge(
                    0, 0, 3, 4, 'QUOTATION SENT', bill_title)
            if rec.state =="sale" or rec.state =="done":
                worksheet.write_merge(
                    0, 0, 3, 4, 'SALES'+'\n'+'ORDER', bill_title)
            if rec.state =="cancel":
                worksheet.write_merge(
                    0, 0, 3, 4, 'CANCELLED'+'\n'+'ORDER', bill_title)
            # company details
            worksheet.write(1, 0, rec.company_id.name or '-', blue_text)
            worksheet.write(2, 0, rec.company_id.street or '-', blue_text)
            address=''
            
            if rec.company_id.street2:
                address+= str(rec.company_id.street2) + ',' 
            if rec.company_id.city:
                address+=str(rec.company_id.city) + ',' 
            if rec.company_id.state_id.name:
                address+=str(rec.company_id.state_id.name) + ','
            if rec.company_id.zip:
                address+=str(rec.company_id.zip) 
            worksheet.write(3, 0, address or '-', blue_text)
            worksheet.write(4, 0, rec.company_id.phone or '-', blue_text)
            worksheet.write(5, 0, rec.company_id.email or '-', blue_text)
            worksheet.write(6, 0, '' or '', blue_text)


            worksheet.write_merge(1, 1, 2, 3, 'SALE ORDER NO.', color_blue)
            worksheet.write(1, 4, 'DATE' or '', color_blue)

            worksheet.write_merge(2, 2, 2, 3, rec.name or '', for_left_not_bold)
            worksheet.write(2, 4, rec.date_order.strftime('%m-%d-%Y') or '', for_left_not_bold)

            worksheet.write_merge(3, 3, 2, 3, 'CUSTOMER ID', color_blue)
            worksheet.write(3, 4, 'TERMS' or '', color_blue)

            worksheet.write_merge(4, 4, 2, 3, rec.partner_id.name or '-', for_left_not_bold)
            worksheet.write(4, 4, rec.payment_term_id.name or '', for_left_not_bold)

            worksheet.write_merge(5, 5, 2, 3, '', for_left_not_bold)
            worksheet.write(5, 5, '' , for_left_not_bold)
            worksheet.write_merge(6, 6, 2, 3, '', for_left_not_bold)
            worksheet.write(6, 6, '' , for_left_not_bold)
      


            # bill to 
            worksheet.write(7, 0, 'BILL TO' or '', color_blue)
            worksheet.write(8, 0, rec.partner_id.name or '-', for_left_not_bold)
            worksheet.write(9, 0, rec.partner_id.street or '-', for_left_not_bold)
            address=''
            
            if rec.partner_id.street2:
                address+= str(rec.partner_id.street2) + ',' 
            if rec.partner_id.city:
                address+=str(rec.partner_id.city) + ',' 
            if rec.partner_id.state_id.name:
                address+=str(rec.partner_id.state_id.name) + ','
            if rec.partner_id.zip:
                address+=str(rec.partner_id.zip)
            
            worksheet.write(10, 0, address or '-', for_left_not_bold)
            worksheet.write(11, 0, rec.partner_id.phone or '-', for_left_not_bold)
            worksheet.write(12, 0, rec.partner_id.email or '-', for_left_not_bold)
            worksheet.write(13, 0, '' or '', for_left_not_bold)

            # ship To 
            worksheet.write_merge(7, 7, 2, 4, 'SHIP TO', color_blue)
            worksheet.write_merge(8, 8, 2, 4, rec.company_id.name or '-', for_left_not_bold)
            worksheet.write_merge(9, 9, 2, 4, rec.company_id.street or '-', for_left_not_bold)
            address=''
            
            if rec.company_id.street2:
                address+= str(rec.company_id.street2) + ',' 
            if rec.company_id.city:
                address+=str(rec.company_id.city) + ',' 
            if rec.company_id.state_id.name:
                address+=str(rec.company_id.state_id.name) + ','
            if rec.company_id.zip:
                address+=str(rec.company_id.zip) 
            worksheet.write_merge(10, 10, 2, 4, address or '-', for_left_not_bold)
            worksheet.write_merge(11, 11, 2, 4, rec.company_id.phone or '-', for_left_not_bold)
            worksheet.write_merge(12, 12, 2, 4, '', for_left_not_bold)
            worksheet.write_merge(13, 13, 2, 4, '', for_left_not_bold)


            # product detail 
            worksheet.write_merge(14,14, 0, 1, 'DESCRIPTION' or '', color_blue)
            worksheet.write(14, 2, 'QTY' or '', color_blue)
            worksheet.write(14, 3, 'UNIT PRICE' or '', color_blue)
            worksheet.write(14, 4, 'AMOUNT' or '', color_blue)

            row =15
            
            for i in rec.order_line:
                if i.display_type:
                    worksheet.write_merge(row,row, 0, 1, i.name or '', for_left_not_bold)
                else:
                    worksheet.write_merge(row,row, 0, 1, i.product_id.display_name or '', for_left_not_bold)

                if i.display_type:
                    worksheet.write(row, 2, '' or '', number_format)
                else:
                    worksheet.write(row, 2, i.product_uom_qty or '0.00', number_format)
                if i.display_type:
                    worksheet.write(row, 3, '' or '', number_format)
                else:
                    worksheet.write(row, 3, i.price_unit or '0.00', number_format)
                if i.display_type:
                    worksheet.write(row, 4, '' or '', number_format)
                else:
                    worksheet.write(row, 4, i.price_subtotal or '0.00', number_format)
                row+=1
               
            

                
                
               
                

            
            # blank space
            row= row+1
            worksheet.write_merge(row,row, 0, 1, '' or '', for_left_not_bold)
            worksheet.write(row, 2, '' or '', for_left_not_bold)
            worksheet.write(row, 3, '' or '', for_left_not_bold)
            worksheet.write(row, 4, '' or '', for_left_not_bold)
            row+=1
            worksheet.write_merge(row,row, 0, 1, '' or '', for_left_not_bold)
            worksheet.write(row, 2, '' or '', for_left_not_bold)
            worksheet.write(row, 3, '' or '', for_left_not_bold)
            worksheet.write(row, 4, '' or '', for_left_not_bold)
            row+=1
            worksheet.write_merge(row,row, 0, 1, '' or '', for_left_not_bold)
            worksheet.write(row, 2, '' or '', for_left_not_bold)
            worksheet.write(row, 3, '' or '', for_left_not_bold)
            worksheet.write(row, 4, '' or '', for_left_not_bold)

            row+=1
             
            # total 
            worksheet.write_merge(row,row+2, 0, 1, 'THANK YOU' or '', Thank_size)
            worksheet.write_merge(row,row, 2,3, 'SUBTOTAL' or '', for_left_not_bold)
            worksheet.write_merge(row+1,row+1, 2,3, 'TAXES' or '', for_left_not_bold)
            worksheet.write_merge(row+2,row+2, 2,3, 'TOTAL' or '', for_left_not_bold)
            symbol=''
            for s in rec.currency_id:
                symbol=s.symbol


            worksheet.write(row, 4, rec.amount_untaxed or '0.00', number_format)
            worksheet.write(row+1, 4, rec.amount_tax or '0.00', number_format)
            worksheet.write(row+2, 4, symbol + ' ' + str(rec.amount_total) or '0.00', number_format)

           
        fp = io.BytesIO()
        workbook.save(fp)
        sale_excel_id = self.env['excel.report'].create({
            'excel_file': base64.b64encode(fp.getvalue()),
            'file_name': filename
        })
        fp.close()

        return{
            'view_mode': 'form',
            'res_id': sale_excel_id.id,
            'res_model': 'excel.report',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }


