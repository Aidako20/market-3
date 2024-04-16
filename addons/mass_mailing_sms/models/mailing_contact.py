#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMailingContact(models.Model):
    _name='mailing.contact'
    _inherit=['mailing.contact','mail.thread.phone']

    mobile=fields.Char(string='Mobile')

    def_sms_get_number_fields(self):
        #TDEnote:shouldoverride_phone_get_number_fieldsbutokassmsisindependencies
        return['mobile']
