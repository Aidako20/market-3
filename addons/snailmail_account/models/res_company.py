#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCompany(models.Model):
    _inherit="res.company"

    invoice_is_snailmail=fields.Boolean(string='SendbyPost',default=False)
