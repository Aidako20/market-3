#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classWebsite(models.Model):
    _inherit='website'

    karma_profile_min=fields.Integer(string="Minimalkarmatoseeotheruser'sprofile",default=150)
