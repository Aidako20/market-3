#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classProductTemplate(models.Model):
    _inherit='product.template'

    l10n_in_hsn_code=fields.Char(string="HSN/SACCode",help="HarmonizedSystemNomenclature/ServicesAccountingCode")
    l10n_in_hsn_description=fields.Char(string="HSN/SACDescription",help="HSN/SACdescriptionisrequiredifHSN/SACcodeisnotprovided.")
