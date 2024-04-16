#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classCity(models.Model):
    _inherit="res.city"

    l10n_pe_code=fields.Char('Code',help='Thiscodewillhelpwiththe'
                               'identificationofeachcityinPeru.')
