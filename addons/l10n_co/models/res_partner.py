#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,api


classResPartner(models.Model):
    _inherit='res.partner'

    @api.constrains('vat','country_id','l10n_latam_identification_type_id')
    defcheck_vat(self):
        #check_vatisimplementedbybase_vatwhichthislocalization
        #doesn'tdirectlydependon.Itishoweverautomatically
        #installedforColombia.
        ifself.sudo().env.ref('base.module_base_vat').state=='installed':
            #don'tcheckColombianpartnersunlesstheyhaveRUT(=ColombianVAT)setasdocumenttype
            self=self.filtered(lambdapartner:partner.country_id.code!="CO"or\
                                                 partner.l10n_latam_identification_type_id.l10n_co_document_code=='rut')
            returnsuper(ResPartner,self).check_vat()
        else:
            returnTrue
