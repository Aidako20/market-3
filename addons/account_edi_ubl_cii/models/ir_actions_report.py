#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.toolsimportcleanup_xml_node

fromlxmlimportetree
importbase64
fromxml.sax.saxutilsimportescape,quoteattr


classIrActionsReport(models.Model):
    _inherit='ir.actions.report'

    def_postprocess_pdf_report(self,record,buffer):
        """
        EXTENDSaccount
        AddthepdfreportinXMLasbase64string.
        """
        result=super()._postprocess_pdf_report(record,buffer)

        ifrecord._name=='account.move':
            #excludeefffbecauseit'shandledbyl10n_be_edi
            format_codes=['ubl_bis3','ubl_de','nlcius_1']
            edi_attachments=record.edi_document_ids.filtered(lambdad:d.edi_format_id.codeinformat_codes).attachment_id
            foredi_attachmentinedi_attachments:
                old_xml=base64.b64decode(edi_attachment.with_context(bin_size=False).datas,validate=True)
                tree=etree.fromstring(old_xml)
                anchor_elements=tree.xpath("//*[local-name()='AccountingSupplierParty']")
                additional_document_elements=tree.xpath("//*[local-name()='AdditionalDocumentReference']")
                #withthisclause,weensurethexmlareonlypostprocessedonce(evenwhentheinvoiceisresetto
                #draftthenvalidatedagain)
                ifanchor_elementsandnotadditional_document_elements:
                    pdf=base64.b64encode(buffer.getvalue()).decode()
                    pdf_name='%s.pdf'%record.name.replace('/','_')
                    to_inject='''
                        <cac:AdditionalDocumentReference
                            xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
                            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                            <cbc:ID>%s</cbc:ID>
                            <cac:Attachment>
                                <cbc:EmbeddedDocumentBinaryObjectmimeCode="application/pdf"filename=%s>
                                    %s
                                </cbc:EmbeddedDocumentBinaryObject>
                            </cac:Attachment>
                        </cac:AdditionalDocumentReference>
                    '''%(escape(pdf_name),quoteattr(pdf_name),pdf)

                    anchor_index=tree.index(anchor_elements[0])
                    tree.insert(anchor_index,etree.fromstring(to_inject))
                    new_xml=etree.tostring(cleanup_xml_node(tree),xml_declaration=True,encoding='UTF-8')
                    edi_attachment.write({
                        'res_model':'account.move',
                        'res_id':record.id,
                        'datas':base64.b64encode(new_xml),
                        'mimetype':'application/xml',
                    })

        returnresult
