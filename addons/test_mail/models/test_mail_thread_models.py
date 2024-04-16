#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMailTestCC(models.Model):
    _name='mail.test.cc'
    _description="TestEmailCCThread"
    _inherit=['mail.thread.cc']

    name=fields.Char()
