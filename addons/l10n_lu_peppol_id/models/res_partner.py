#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResPartner(models.Model):
    _inherit='res.partner'

    country_code=fields.Char(related='country_id.code')
    l10n_lu_peppol_identifier=fields.Char("PeppolUniqueIdentifier")
