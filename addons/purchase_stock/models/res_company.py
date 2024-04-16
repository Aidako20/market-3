#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit='res.company'

    days_to_purchase=fields.Float(
        string='DaystoPurchase',
        help="DaysneededtoconfirmaPO,definewhenaPOshouldbevalidated")
