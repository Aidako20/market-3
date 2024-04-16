#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,models,fields,tools,_
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT,float_repr
fromflectra.tests.commonimportForm
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression

frompathlibimportPureWindowsPath

importlogging

_logger=logging.getLogger(__name__)


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    def_create_invoice_from_ubl(self,tree):
        invoice=self.env['account.move']
        journal=invoice._get_default_journal()

        move_type='out_invoice'ifjournal.type=='sale'else'in_invoice'
        element=tree.find('.//{*}InvoiceTypeCode')
        ifelementisnotNoneandelement.text=='381':
            move_type='in_refund'ifmove_type=='in_invoice'else'out_refund'

        invoice=invoice.with_context(default_move_type=move_type,default_journal_id=journal.id)
        returnself._import_ubl(tree,invoice)

    def_update_invoice_from_ubl(self,tree,invoice):
        invoice=invoice.with_context(default_move_type=invoice.move_type,default_journal_id=invoice.journal_id.id)
        returnself._import_ubl(tree,invoice)

    def_import_ubl(self,tree,invoice):
        """DecodesanUBLinvoiceintoaninvoice.

        :paramtree:   theUBLtreetodecode.
        :paraminvoice:theinvoicetoupdateoranemptyrecordset.
        :returns:      theinvoicewheretheUBLdatawasimported.
        """

        def_get_ubl_namespaces():
            '''Ifthenamespaceisdeclaredwithxmlns='...',thenamespacesmapcontainsthe'None'keythatcausesan
            TypeError:emptynamespaceprefixisnotsupportedinXPath
            Then,weneedtoremaparbitrarilythiskey.

            :paramtree:Aninstanceofetree.
            :return:Thenamespacesmapwithout'None'key.
            '''
            namespaces=tree.nsmap
            namespaces['inv']=namespaces.pop(None)
            returnnamespaces

        namespaces=_get_ubl_namespaces()

        def_find_value(xpath,element=tree):
            returnself._find_value(xpath,element,namespaces)

        withForm(invoice)asinvoice_form:
            self_ctx=self.with_company(invoice.company_id.id)

            #Reference
            elements=tree.xpath('//cbc:ID',namespaces=namespaces)
            ifelements:
                invoice_form.ref=elements[0].text
            elements=tree.xpath('//cbc:InstructionID',namespaces=namespaces)
            ifelements:
                invoice_form.payment_reference=elements[0].text

            #Dates
            elements=tree.xpath('//cbc:IssueDate',namespaces=namespaces)
            ifelements:
                invoice_form.invoice_date=elements[0].text
            elements=tree.xpath('//cbc:PaymentDueDate',namespaces=namespaces)
            ifelements:
                invoice_form.invoice_date_due=elements[0].text
            #allowbothcbc:PaymentDueDateandcbc:DueDate
            elements=tree.xpath('//cbc:DueDate',namespaces=namespaces)
            invoice_form.invoice_date_due=invoice_form.invoice_date_dueorelementsandelements[0].text

            #Currency
            elements=tree.xpath('//cbc:DocumentCurrencyCode',namespaces=namespaces)
            currency_code=elementsandelements[0].textor''
            currency=self.env['res.currency'].search([('name','=',currency_code.upper())],limit=1)
            ifelements:
                invoice_form.currency_id=currency

            #Incoterm
            elements=tree.xpath('//cbc:TransportExecutionTerms/cac:DeliveryTerms/cbc:ID',namespaces=namespaces)
            ifelements:
                invoice_form.invoice_incoterm_id=self.env['account.incoterms'].search([('code','=',elements[0].text)],limit=1)

            #Partner
            counterpart='Customer'ifinvoice_form.move_typein('out_invoice','out_refund')else'Supplier'
            invoice_form.partner_id=self_ctx._retrieve_partner(
                name=_find_value(f'//cac:Accounting{counterpart}Party/cac:Party//cbc:Name'),
                phone=_find_value(f'//cac:Accounting{counterpart}Party/cac:Party//cbc:Telephone'),
                mail=_find_value(f'//cac:Accounting{counterpart}Party/cac:Party//cbc:ElectronicMail'),
                vat=_find_value(f'//cac:Accounting{counterpart}Party/cac:Party//cbc:CompanyID'),
            )

            #Lines
            lines_elements=tree.xpath('//cac:InvoiceLine',namespaces=namespaces)
            forelineinlines_elements:
                withinvoice_form.invoice_line_ids.new()asinvoice_line_form:
                    #Product
                    invoice_line_form.product_id=self_ctx._retrieve_product(
                        default_code=_find_value('cac:Item/cac:SellersItemIdentification/cbc:ID',eline),
                        name=_find_value('cac:Item/cbc:Name',eline),
                        barcode=_find_value('cac:Item/cac:StandardItemIdentification/cbc:ID[@schemeID=\'0160\']',eline)
                    )

                    #Quantity
                    elements=eline.xpath('cbc:InvoicedQuantity',namespaces=namespaces)
                    quantity=elementsandfloat(elements[0].text)or1.0
                    invoice_line_form.quantity=quantity

                    #PriceUnit
                    elements=eline.xpath('cac:Price/cbc:PriceAmount',namespaces=namespaces)
                    price_unit=elementsandfloat(elements[0].text)or0.0
                    elements=eline.xpath('cbc:LineExtensionAmount',namespaces=namespaces)
                    line_extension_amount=elementsandfloat(elements[0].text)or0.0
                    invoice_line_form.price_unit=price_unitorline_extension_amount/invoice_line_form.quantityor0.0

                    #Name
                    elements=eline.xpath('cac:Item/cbc:Description',namespaces=namespaces)
                    ifelementsandelements[0].text:
                        invoice_line_form.name=elements[0].text
                        invoice_line_form.name=invoice_line_form.name.replace('%month%',str(fields.Date.to_date(invoice_form.invoice_date).month)) #TODO:fullnameinlocale
                        invoice_line_form.name=invoice_line_form.name.replace('%year%',str(fields.Date.to_date(invoice_form.invoice_date).year))
                    else:
                        partner_name=_find_value('//cac:AccountingSupplierParty/cac:Party//cbc:Name')
                        invoice_line_form.name="%s(%s)"%(partner_nameor'',invoice_form.invoice_date)

                    #Taxes
                    tax_element=eline.xpath('cac:TaxTotal/cac:TaxSubtotal',namespaces=namespaces)
                    invoice_line_form.tax_ids.clear()
                    forelineintax_element:
                        tax=self_ctx._retrieve_tax(
                            amount=_find_value('cbc:Percent',eline),
                            type_tax_use=invoice_form.journal_id.type
                        )
                        iftax:
                            invoice_line_form.tax_ids.add(tax)
        invoice=invoice_form.save()

        #RegeneratePDF
        attachments=self.env['ir.attachment']
        elements=tree.xpath('//cac:AdditionalDocumentReference',namespaces=namespaces)
        forelementinelements:
            attachment_name=element.xpath('cbc:ID',namespaces=namespaces)
            attachment_data=element.xpath('cac:Attachment//cbc:EmbeddedDocumentBinaryObject',namespaces=namespaces)
            ifattachment_nameandattachment_data:
                text=attachment_data[0].text
                #Normalizethenameofthefile:somee-fffemittersputthefullpathofthefile
                #(WindowsorLinuxstyle)and/orthenameofthexmlinsteadofthepdf.
                #Getonlythefilenamewithapdfextension.
                name=PureWindowsPath(attachment_name[0].text).stem+'.pdf'
                attachments|=self.env['ir.attachment'].create({
                    'name':name,
                    'res_id':invoice.id,
                    'res_model':'account.move',
                    'datas':text+'='*(len(text)%3), #Fixincorrectpadding
                    'type':'binary',
                    'mimetype':'application/pdf',
                })
        ifattachments:
            invoice.with_context(no_new_invoice=True).message_post(attachment_ids=attachments.ids)

        returninvoice
