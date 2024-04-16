#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    l10n_eu_services_eu_country=fields.Boolean('IsEuropeancountry?',compute='_compute_l10n_eu_services_european_country')

    defrefresh_eu_tax_mapping(self):
        self.env.companies._map_eu_taxes()

    @api.depends('company_id')
    def_compute_l10n_eu_services_european_country(self):
        european_countries=self.env.ref('base.europe').country_ids
        forrecordinself:
            record.l10n_eu_services_eu_country=record.company_id.account_tax_fiscal_country_idineuropean_countries
