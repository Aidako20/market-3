#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

classCompany(models.Model):
    _inherit="res.company"

    snailmail_color=fields.Boolean(string='Color',default=True)
    snailmail_cover=fields.Boolean(string='AddaCoverPage',default=False)
    snailmail_duplex=fields.Boolean(string='Bothsides',default=False)
