#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classCompany(models.Model):
    _inherit='res.company'

    lunch_minimum_threshold=fields.Float()
