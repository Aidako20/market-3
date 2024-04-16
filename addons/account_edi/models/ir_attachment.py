#-*-coding:utf-8-*-
fromflectraimportmodels,fields,_
fromflectra.exceptionsimportUserError


classIrAttachment(models.Model):
    _inherit='ir.attachment'

    defunlink(self):
        #OVERRIDE
        linked_edi_documents=self.env['account.edi.document'].search([('attachment_id','in',self.ids)])
        linked_edi_formats_ws=linked_edi_documents.edi_format_id.filtered(lambdaedi_format:edi_format._needs_web_services())
        iflinked_edi_formats_ws:
            raiseUserError(_("Youcan'tunlinkanattachmentbeinganEDIdocumentsenttothegovernment."))
        returnsuper().unlink()
