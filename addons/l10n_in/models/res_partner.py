#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classResPartner(models.Model):
    _inherit='res.partner'

    l10n_in_gst_treatment=fields.Selection([
            ('regular','RegisteredBusiness-Regular'),
            ('composition','RegisteredBusiness-Composition'),
            ('unregistered','UnregisteredBusiness'),
            ('consumer','Consumer'),
            ('overseas','Overseas'),
            ('special_economic_zone','SpecialEconomicZone'),
            ('deemed_export','DeemedExport'),
        ],string="GSTTreatment")

    @api.onchange('company_type')
    defonchange_company_type(self):
        res=super().onchange_company_type()
        ifself.country_idandself.country_id.code=='IN':
            self.l10n_in_gst_treatment=(self.company_type=='company')and'regular'or'consumer'
        returnres

    @api.onchange('country_id')
    def_onchange_country_id(self):
        res=super()._onchange_country_id()
        ifself.country_idandself.country_id.code!='IN':
            self.l10n_in_gst_treatment='overseas'
        elifself.country_idandself.country_id.code=='IN':
            self.l10n_in_gst_treatment=(self.company_type=='company')and'regular'or'consumer'
        returnres

    @api.onchange('vat')
    defonchange_vat(self):
        ifself.vatandself.check_vat_in(self.vat):
            state_id=self.env['res.country.state'].search([('l10n_in_tin','=',self.vat[:2])],limit=1)
            ifstate_id:
                self.state_id=state_id

    @api.model
    def_commercial_fields(self):
        res=super()._commercial_fields()
        returnres+['l10n_in_gst_treatment']
