#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAccountTax(models.Model):
    _inherit="account.tax"

    l10n_ph_atc=fields.Char("PhilippinesATC")
