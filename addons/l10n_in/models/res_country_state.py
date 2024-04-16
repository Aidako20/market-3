#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCountryState(models.Model):
    _inherit='res.country.state'

    l10n_in_tin=fields.Char('TINNumber',size=2,help="TINnumber-firsttwodigits")
