#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAccountTaxTemplate(models.Model):
    _inherit="account.tax.template"

    l10n_ph_atc=fields.Char("PhilippinesATC")

    def_get_tax_vals(self,company,tax_template_to_tax):
        val=super()._get_tax_vals(company,tax_template_to_tax)
        val.update({"l10n_ph_atc":self.l10n_ph_atc})
        returnval
