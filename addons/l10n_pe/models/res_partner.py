#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails
fromflectraimportfields,models,api


classResPartner(models.Model):
    _inherit='res.partner'

    l10n_pe_district=fields.Many2one(
        'l10n_pe.res.city.district',string='District',
        help='Districtsarepartofaprovinceorcity.')

    @api.onchange('l10n_pe_district')
    def_onchange_l10n_pe_district(self):
        ifself.l10n_pe_district:
            self.city_id=self.l10n_pe_district.city_id

    @api.onchange('city_id')
    def_onchange_l10n_pe_city_id(self):
        ifself.city_idandself.l10n_pe_district.city_idandself.l10n_pe_district.city_id!=self.city_id:
            self.l10n_pe_district=False
