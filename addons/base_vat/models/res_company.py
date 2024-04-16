#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit='res.company'

    vat_check_vies=fields.Boolean(string='VerifyVATNumbers')
