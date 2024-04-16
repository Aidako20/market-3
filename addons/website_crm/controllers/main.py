#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.website_form.controllers.mainimportWebsiteForm


classWebsiteForm(WebsiteForm):

    def_get_country(self):
        country_code=request.session.geoipandrequest.session.geoip.get('country_code')orFalse
        ifcountry_code:
            returnrequest.env['res.country'].sudo().search([('code','=',country_code)],limit=1)
        returnrequest.env['res.country']

    def_get_phone_fields_to_validate(self):
        return['phone','mobile']

    #Checkandinsertvaluesfromtheformonthemodel<model>+validationphonefields
    def_handle_website_form(self,model_name,**kwargs):
        model_record=request.env['ir.model'].sudo().search([('model','=',model_name),('website_form_access','=',True)])
        ifmodel_recordandhasattr(request.env[model_name],'phone_format'):
            try:
                data=self.extract_data(model_record,request.params)
            except:
                #nospecificmanagement,superwilldoit
                pass
            else:
                record=data.get('record',{})
                phone_fields=self._get_phone_fields_to_validate()
                country=request.env['res.country'].browse(record.get('country_id'))
                contact_country=country.exists()andcountryorself._get_country()
                forphone_fieldinphone_fields:
                    ifnotrecord.get(phone_field):
                        continue
                    number=record[phone_field]
                    fmt_number=request.env[model_name].phone_format(number,contact_country)
                    request.params.update({phone_field:fmt_number})

        ifmodel_name=='crm.lead'andnotrequest.params.get('state_id'):
            geoip_country_code=request.session.get('geoip',{}).get('country_code')
            geoip_state_code=request.session.get('geoip',{}).get('region')
            ifgeoip_country_codeandgeoip_state_code:
                state=request.env['res.country.state'].search([('code','=',geoip_state_code),('country_id.code','=',geoip_country_code)])
                ifstate:
                    request.params['state_id']=state.id
        returnsuper(WebsiteForm,self)._handle_website_form(model_name,**kwargs)

    definsert_record(self,request,model,values,custom,meta=None):
        is_lead_model=model.model=='crm.lead'
        ifis_lead_model:
            if'company_id'notinvalues:
                values['company_id']=request.website.company_id.id
            lang=request.context.get('lang',False)
            values['lang_id']=values.get('lang_id')orrequest.env['res.lang']._lang_get_id(lang)

        result=super(WebsiteForm,self).insert_record(request,model,values,custom,meta=meta)

        ifis_lead_model:
            visitor_sudo=request.env['website.visitor']._get_visitor_from_request()
            ifvisitor_sudoandresult:
                lead_sudo=request.env['crm.lead'].browse(result).sudo()
                iflead_sudo.exists():
                    vals={'lead_ids':[(4,result)]}
                    ifnotvisitor_sudo.lead_idsandnotvisitor_sudo.partner_id:
                        vals['name']=lead_sudo.contact_name
                    visitor_sudo.write(vals)
        returnresult
