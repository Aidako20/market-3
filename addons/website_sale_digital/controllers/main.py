#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importio
importos
importmimetypes
fromwerkzeug.utilsimportredirect

fromflectraimporthttp
fromflectra.exceptionsimportAccessError
fromflectra.httpimportrequest
fromflectra.addons.sale.controllers.portalimportCustomerPortal
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale


classWebsiteSaleDigitalConfirmation(WebsiteSale):
    @http.route([
        '/shop/confirmation',
    ],type='http',auth="public",website=True)
    defpayment_confirmation(self,**post):
        response=super(WebsiteSaleDigitalConfirmation,self).payment_confirmation(**post)
        order_lines=response.qcontext['order'].order_line
        digital_content=any(x.product_id.type=='digital'forxinorder_lines)
        response.qcontext.update(digital=digital_content)
        returnresponse


classWebsiteSaleDigital(CustomerPortal):
    orders_page='/my/orders'

    @http.route([
        '/my/orders/<int:order_id>',
    ],type='http',auth='public',website=True)
    defportal_order_page(self,order_id=None,**post):
        response=super(WebsiteSaleDigital,self).portal_order_page(order_id=order_id,**post)
        ifnot'sale_order'inresponse.qcontext:
            returnresponse
        order=response.qcontext['sale_order']
        invoiced_lines=request.env['account.move.line'].sudo().search([('move_id','in',order.invoice_ids.ids),('move_id.payment_state','in',['paid','in_payment'])])
        products=invoiced_lines.mapped('product_id')|order.order_line.filtered(lambdar:notr.price_subtotal).mapped('product_id')
        ifnotorder.amount_total:
            #inthatcase,weshouldaddalldownloadlinkstotheproducts
            #sincethereisnothingtopay,soweshouldn'twaitforaninvoice
            products=order.order_line.mapped('product_id')

        Attachment=request.env['ir.attachment'].sudo()
        purchased_products_attachments={}
        forproductinproducts.filtered(lambdap:p.attachment_count):
            #Searchforproductattachments
            product_id=product.id
            template=product.product_tmpl_id
            att=Attachment.sudo().search_read(
                domain=['|','&',('res_model','=',product._name),('res_id','=',product_id),'&',('res_model','=',template._name),('res_id','=',template.id),('product_downloadable','=',True)],
                fields=['name','write_date'],
                order='write_datedesc',
            )

            #Ignoreproductswithnoattachments
            ifnotatt:
                continue

            purchased_products_attachments[product_id]=att

        response.qcontext.update({
            'digital_attachments':purchased_products_attachments,
        })
        returnresponse

    @http.route([
        '/my/download',
    ],type='http',auth='public')
    defdownload_attachment(self,attachment_id):
        #Checkifthisisavalidattachmentid
        attachment=request.env['ir.attachment'].sudo().search_read(
            [('id','=',int(attachment_id))],
            ["name","datas","mimetype","res_model","res_id","type","url"]
        )

        ifattachment:
            attachment=attachment[0]
        else:
            returnredirect(self.orders_page)

        try:
            request.env['ir.attachment'].browse(attachment_id).check('read')
        exceptAccessError: #Theuserdoesnothavereadaccessontheattachment.
            #Checkifaccesscanbegrantedthroughtheirpurchases.
            res_model=attachment['res_model']
            res_id=attachment['res_id']
            digital_purchases=request.env['account.move.line'].get_digital_purchases()
            ifres_model=='product.product':
                purchased_product_ids=digital_purchases
            elifres_model=='product.template':
                purchased_product_ids=request.env['product.product'].sudo().browse(
                    digital_purchases
                ).mapped('product_tmpl_id').ids
            else:
                purchased_product_ids=[] #Thepurchasesmustberelatedtoproducts.
            ifres_idnotinpurchased_product_ids: #Norelatedpurchasewasfound.
                returnredirect(self.orders_page) #Preventtheuserfromdownloading.

        #Theuserhasboughttheproduct,orhastherightstotheattachment
        ifattachment["type"]=="url":
            ifattachment["url"]:
                returnredirect(attachment["url"])
            else:
                returnrequest.not_found()
        elifattachment["datas"]:
            data=io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            #wefollowwhatisdoneinir_http'sbinary_contentfortheextensionmanagement
            extension=os.path.splitext(attachment["name"]or'')[1]
            extension=extensionifextensionelsemimetypes.guess_extension(attachment["mimetype"]or'')
            filename=attachment['name']
            filename=filenameifos.path.splitext(filename)[1]elsefilename+extension
            returnhttp.send_file(data,filename=filename,as_attachment=True)
        else:
            returnrequest.not_found()
