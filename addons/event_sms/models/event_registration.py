#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classRegistration(models.Model):
    _inherit='event.registration'

    def_sms_get_number_fields(self):
        """Thismethodreturnsthefieldstousetofindthenumbertouseto
        sendanSMSonarecord."""
        return['mobile','phone']
