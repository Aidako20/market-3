#-*-coding:utf-8-*-

fromflectraimportmodels,api,_
fromflectra.exceptionsimportUserError

fromflectra.toolsimportfloat_compare


classIrActionsReport(models.Model):
    _inherit='ir.actions.report'

    defretrieve_attachment(self,record):
        #gettheoriginalbillsthroughthemessage_main_attachment_idfieldoftherecord
        ifself.report_name=='account.report_original_vendor_bill'andrecord.message_main_attachment_id:
            ifrecord.message_main_attachment_id.mimetype=='application/pdf'or\
               record.message_main_attachment_id.mimetype.startswith('image'):
                returnrecord.message_main_attachment_id
        returnsuper(IrActionsReport,self).retrieve_attachment(record)

    def_post_pdf(self,save_in_attachment,pdf_content=None,res_ids=None):
        #don'tincludethegenerateddummyreport
        ifself.report_name=='account.report_original_vendor_bill':
            pdf_content=None
            res_ids=None
            ifnotsave_in_attachment:
                raiseUserError(_("Nooriginalvendorbillscouldbefoundforanyoftheselectedvendorbills."))
        returnsuper(IrActionsReport,self)._post_pdf(save_in_attachment,pdf_content=pdf_content,res_ids=res_ids)

    def_postprocess_pdf_report(self,record,buffer):
        #don'tsavethe'account.report_original_vendor_bill'reportasit'sjustameantoprintexistingattachments
        ifself.report_name=='account.report_original_vendor_bill':
            returnNone
        res=super(IrActionsReport,self)._postprocess_pdf_report(record,buffer)
        ifself.model=='account.move'andrecord.state=='posted'andrecord.is_sale_document(include_receipts=True):
            attachment=self.retrieve_attachment(record)
            ifattachment:
                attachment.register_as_main_attachment(force=False)
        returnres

    def_render_qweb_pdf(self,res_ids=None,data=None):
        #Overriddensothattheprint>invoicesactionsraisesanerror
        #whentryingtoprintamiscellaneousoperationinsteadofaninvoice.
        #+appendcontextdatawiththedisplay_name_in_footerparameter
        ifself.model=='account.move'andres_ids:
            invoice_reports=(self.env.ref('account.account_invoices_without_payment'),self.env.ref('account.account_invoices'))
            ifselfininvoice_reports:
                ifself.env['ir.config_parameter'].sudo().get_param('account.display_name_in_footer'):
                    data=dataanddict(data)or{}
                    data.update({'display_name_in_footer':True})
                moves=self.env['account.move'].browse(res_ids)
                ifany(notmove.is_invoice(include_receipts=True)formoveinmoves):
                    raiseUserError(_("Onlyinvoicescouldbeprinted."))

        returnsuper()._render_qweb_pdf(res_ids=res_ids,data=data)

    def_get_rendering_context(self,docids,data):
        data=dataanddict(data)or{}
        data.update({'float_compare':float_compare})
        returnsuper()._get_rendering_context(docids=docids,data=data)
