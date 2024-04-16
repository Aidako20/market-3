#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classAccountTax(models.Model):
    _name='account.tax'
    _inherit='account.tax'

    l10n_cl_sii_code=fields.Integer('SIICode',group_operator=False)


classAccountTaxTemplate(models.Model):
    _name='account.tax.template'
    _inherit='account.tax.template'

    l10n_cl_sii_code=fields.Integer('SIICode')

    def_get_tax_vals(self,company,tax_template_to_tax):
        self.ensure_one()
        vals=super(AccountTaxTemplate,self)._get_tax_vals(company,tax_template_to_tax)
        vals.update({
            'l10n_cl_sii_code':self.l10n_cl_sii_code,
        })
        ifself.tax_group_id:
            vals['tax_group_id']=self.tax_group_id.id
        returnvals
