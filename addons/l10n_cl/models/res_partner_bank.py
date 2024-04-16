#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResBank(models.Model):
    _name='res.bank'
    _inherit='res.bank'

    l10n_cl_sbif_code=fields.Char('Cod.SBIF',size=10)
