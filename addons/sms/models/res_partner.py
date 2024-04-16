#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classResPartner(models.Model):
    _name='res.partner'
    _inherit=['res.partner','mail.thread.phone']

    def_sms_get_default_partners(self):
        """Overrideofmail.threadmethod.
            SMSrecipientsonpartnersarethepartnersthemselves.
        """
        returnself

    def_sms_get_number_fields(self):
        """Thismethodreturnsthefieldstousetofindthenumbertouseto
        sendanSMSonarecord."""
        #TDEnote:shouldoverride_phone_get_number_fieldsbutokassmsoverrideit
        return['mobile','phone']
