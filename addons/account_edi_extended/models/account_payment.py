#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classAccountPayment(models.Model):
    _inherit='account.payment'

    defaction_retry_edi_documents_error(self):
        self.ensure_one()
        returnself.move_id.action_retry_edi_documents_error()
