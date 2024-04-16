#-*-coding:utf-8-*-

fromflectraimportapi,models


classMailTemplate(models.Model):
    _inherit="mail.template"

    def_get_edi_attachments(self,document):
        """
        Willreturntheinformationabouttheattachmentoftheedidocumentforaddingtheattachmentinthemail.
        Canbeoverriddenwheree.g.azip-fileneedstobesentwiththeindividualfilesinsteadoftheentirezip
        :paramdocument:anedidocument
        :return:listwithatuplewiththenameandbase64contentoftheattachment
        """
        ifnotdocument.attachment_id:
            return[]
        return[(document.attachment_id.name,document.attachment_id.datas)]

    defgenerate_email(self,res_ids,fields):
        res=super().generate_email(res_ids,fields)

        multi_mode=True
        ifisinstance(res_ids,int):
            res_ids=[res_ids]
            multi_mode=False

        ifself.modelnotin['account.move','account.payment']:
            returnres

        records=self.env[self.model].browse(res_ids)
        forrecordinrecords:
            record_data=(res[record.id]ifmulti_modeelseres)
            fordocinrecord.edi_document_ids:

                #TheEDIformatwillbeembeddeddirectlyinsidethePDFandthen,don'tneedtobeaddedtothe
                #wizard.
                ifdoc.edi_format_id._is_embedding_to_invoice_pdf_needed():
                    continue
                record_data.setdefault('attachments',[])
                record_data['attachments']+=self._get_edi_attachments(doc)

        returnres
