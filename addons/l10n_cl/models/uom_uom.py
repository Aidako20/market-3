#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_


classUomUom(models.Model):
    _inherit='uom.uom'

    l10n_cl_sii_code=fields.Char('SIICode')
