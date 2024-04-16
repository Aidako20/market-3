#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classIrActionsReport(models.Model):
    _inherit='ir.actions.report'

    def_post_pdf(self,save_in_attachment,pdf_content=None,res_ids=None):
        #OVERRIDEtoembedsomeEDIdocumentsinsidethePDF.
        ifself.model=='account.move'andres_idsandlen(res_ids)==1andpdf_content:
            invoice=self.env['account.move'].browse(res_ids)
            ifinvoice.is_sale_document()andinvoice.state!='draft':
                pdf_content=invoice.journal_id.edi_format_ids._embed_edis_to_pdf(pdf_content,invoice)

        returnsuper(IrActionsReport,self)._post_pdf(save_in_attachment,pdf_content=pdf_content,res_ids=res_ids)
