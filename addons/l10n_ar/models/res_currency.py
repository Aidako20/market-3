#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResCurrency(models.Model):

    _inherit="res.currency"

    l10n_ar_afip_code=fields.Char('AFIPCode',size=4,help='Thiscodewillbeusedonelectronicinvoice')
