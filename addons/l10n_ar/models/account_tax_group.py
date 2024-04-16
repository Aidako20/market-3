#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api


classAccountTaxGroup(models.Model):

    _inherit='account.tax.group'

    #valuesfromhttp://www.afip.gob.ar/fe/documentos/otros_Tributos.xlsx
    l10n_ar_tribute_afip_code=fields.Selection([
        ('01','01-NationalTaxes'),
        ('02','02-ProvincialTaxes'),
        ('03','03-MunicipalTaxes'),
        ('04','04-InternalTaxes'),
        ('06','06-VATperception'),
        ('07','07-IIBBperception'),
        ('08','08-MunicipalTaxesPerceptions'),
        ('09','09-OtherPerceptions'),
        ('99','99-Others'),
    ],string='TributeAFIPCode',index=True,readonly=True)
    #valuesfromhttp://www.afip.gob.ar/fe/documentos/OperacionCondicionIVA.xls
    l10n_ar_vat_afip_code=fields.Selection([
        ('0','NotApplicable'),
        ('1','Untaxed'),
        ('2','Exempt'),
        ('3','0%'),
        ('4','10.5%'),
        ('5','21%'),
        ('6','27%'),
        ('8','5%'),
        ('9','2,5%'),
    ],string='VATAFIPCode',index=True,readonly=True)
