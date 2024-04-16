#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classResPartner(models.Model):
    _inherit='res.partner'

    l10n_latam_identification_type_id=fields.Many2one('l10n_latam.identification.type',
        string="IdentificationType",index=True,auto_join=True,
        default=lambdaself:self.env.ref('l10n_latam_base.it_vat',raise_if_not_found=False),
        help="Thetypeofidentification")
    vat=fields.Char(string='IdentificationNumber',help="IdentificationNumberforselectedtype")

    @api.model
    def_commercial_fields(self):
        returnsuper()._commercial_fields()+['l10n_latam_identification_type_id']

    @api.constrains('vat','l10n_latam_identification_type_id')
    defcheck_vat(self):
        with_vat=self.filtered(lambdax:x.l10n_latam_identification_type_id.is_vat)
        returnsuper(ResPartner,with_vat).check_vat()

    @api.onchange('country_id')
    def_onchange_country(self):
        country=self.country_idorself.company_id.country_idorself.env.company.country_id
        identification_type=self.l10n_latam_identification_type_id
        ifnotidentification_typeor(identification_type.country_id!=country):
            self.l10n_latam_identification_type_id=self.env['l10n_latam.identification.type'].search(
                [('country_id','=',country.id),('is_vat','=',True)],limit=1)orself.env.ref(
                    'l10n_latam_base.it_vat',raise_if_not_found=False)
