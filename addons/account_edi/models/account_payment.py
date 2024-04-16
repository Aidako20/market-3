#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_


classAccountPayment(models.Model):
    _inherit='account.payment'

    defaction_process_edi_web_services(self):
        returnself.move_id.action_process_edi_web_services()
