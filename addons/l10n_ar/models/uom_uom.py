#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classUom(models.Model):

    _inherit='uom.uom'

    l10n_ar_afip_code=fields.Char('AFIPCode',help='Thiscodewillbeusedonelectronicinvoice')
