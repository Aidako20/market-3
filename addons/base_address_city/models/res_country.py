#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCountry(models.Model):
    _inherit='res.country'

    enforce_cities=fields.Boolean(
        string='EnforceCities',
        help="Checkthisboxtoensureeveryaddresscreatedinthatcountryhasa'City'chosen"
             "inthelistofthecountry'scities.")
