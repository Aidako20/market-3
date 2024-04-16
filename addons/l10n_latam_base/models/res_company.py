#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classResCompany(models.Model):
    _inherit='res.company'

    @api.model
    defcreate(self,vals):
        """Ifexists,usespecificvatidentification.typeforthecountryofthecompany"""
        country_id=vals.get('country_id')
        ifcountry_id:
            country_vat_type=self.env['l10n_latam.identification.type'].search(
                [('is_vat','=',True),('country_id','=',country_id)],limit=1)
            ifcountry_vat_type:
                self=self.with_context(default_l10n_latam_identification_type_id=country_vat_type.id)
        returnsuper().create(vals)
