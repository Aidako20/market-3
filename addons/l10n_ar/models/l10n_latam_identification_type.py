#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classL10nLatamIdentificationType(models.Model):

    _inherit="l10n_latam.identification.type"

    l10n_ar_afip_code=fields.Char("AFIPCode")
