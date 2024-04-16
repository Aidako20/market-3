#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classPhoneMixin(models.AbstractModel):
    _inherit='mail.thread.phone'

    def_phone_get_number_fields(self):
        """Addfieldscomingfromsmsimplementation."""
        sms_fields=self._sms_get_number_fields()
        res=super(PhoneMixin,self)._phone_get_number_fields()
        forfnamein(fforfinresiffnotinsms_fields):
            sms_fields.append(fname)
        returnsms_fields
