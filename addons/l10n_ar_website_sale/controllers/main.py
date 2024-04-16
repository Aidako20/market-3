#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimport_
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.httpimportrequest,route


classL10nARWebsiteSale(WebsiteSale):

    def_get_mandatory_fields_billing(self,country_id=False):
        """Extendmandatoryfieldstoaddnewidentificationandresponsibilityfieldswhencompanyisargentina"""
        res=super()._get_mandatory_fields_billing(country_id)
        ifrequest.website.sudo().company_id.country_id.code=="AR":
            res+=["l10n_latam_identification_type_id","l10n_ar_afip_responsibility_type_id","vat"]
        returnres

    def_get_country_related_render_values(self,kw,render_values):
        res=super()._get_country_related_render_values(kw,render_values)
        ifrequest.website.sudo().company_id.country_id.code=="AR":
            res.update({'identification':kw.get('l10n_latam_identification_type_id'),
                        'responsibility':kw.get('l10n_ar_afip_responsibility_type_id'),
                        'responsibility_types':request.env['l10n_ar.afip.responsibility.type'].search([]),
                        'identification_types':request.env['l10n_latam.identification.type'].search(
                            ['|',('country_id','=',False),('country_id.code','=','AR')])})
        returnres

    def_get_vat_validation_fields(self,data):
        res=super()._get_vat_validation_fields(data)
        ifrequest.website.sudo().company_id.country_id.code=="AR":
            res.update({'l10n_latam_identification_type_id':int(data['l10n_latam_identification_type_id'])
                                                             ifdata.get('l10n_latam_identification_type_id')elseFalse})
            res.update({'name':data['name']ifdata.get('name')elseFalse})
        returnres

    defcheckout_form_validate(self,mode,all_form_values,data):
        """Weextendthemethodtoaddanewvalidation.IfAFIPResposibilityis:

        *FinalConsumerorForeignCustomer:thenitcanselectanyidentificationtype.
        *Anyother(Monotributista,RI,etc):shouldselectalways"CUIT"identificationtype"""
        error,error_message=super().checkout_form_validate(mode,all_form_values,data)

        #IdentificationtypeandAFIPResponsibilityCombination
        ifrequest.website.sudo().company_id.country_id.code=="AR":
            ifmode[1]=='billing':
                iferrorandany(fieldinerrorforfieldin['l10n_latam_identification_type_id','l10n_ar_afip_responsibility_type_id']):
                    returnerror,error_message
                id_type_id=data.get("l10n_latam_identification_type_id")
                afip_resp_id=data.get("l10n_ar_afip_responsibility_type_id")

                id_type=request.env['l10n_latam.identification.type'].browse(id_type_id)ifid_type_idelseFalse
                afip_resp=request.env['l10n_ar.afip.responsibility.type'].browse(afip_resp_id)ifafip_resp_idelseFalse
                cuit_id_type=request.env.ref('l10n_ar.it_cuit')

                #CheckiftheAFIPresponsibilityisdifferentfromFinalConsumerorForeignCustomer,
                #andiftheidentificationtypeisdifferentfromCUIT
                ifafip_resp.codenotin['5','9']andid_type!=cuit_id_type:
                    error["l10n_latam_identification_type_id"]='error'
                    error_message.append(_('FortheselectedAFIPResponsibilityyouwillneedtosetCUITIdentificationType'))

        returnerror,error_message
