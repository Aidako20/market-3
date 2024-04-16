#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimport_,api,fields,models


classResCurrency(models.Model):
    _name="res.currency"
    _inherit="res.currency"

    l10n_cl_currency_code=fields.Char('CurrencyCode')
    l10n_cl_short_name=fields.Char('ShortName')
