#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResPartner(models.Model):
    _name='res.country'
    _inherit='res.country'

    l10n_cl_customs_code=fields.Char('CustomsCode')
    l10n_cl_customs_name=fields.Char('CustomsName')
    l10n_cl_customs_abbreviation=fields.Char('CustomsAbbreviation')
