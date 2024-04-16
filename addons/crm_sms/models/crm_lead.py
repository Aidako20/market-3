#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classCrmLead(models.Model):
    _inherit='crm.lead'

    def_sms_get_number_fields(self):
        """Thismethodreturnsthefieldstousetofindthenumbertouseto
        sendanSMSonarecord."""
        #TDEFIXME:tobecleanedin14.4+asitconflictswith_phone_get_number_fields
        return['mobile','phone']
