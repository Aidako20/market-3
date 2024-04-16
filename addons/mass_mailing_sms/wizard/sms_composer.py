#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug.urls

fromflectraimportfields,models,_


classSMSComposer(models.TransientModel):
    _inherit='sms.composer'

    #massmodewithmasssms
    mass_sms_allow_unsubscribe=fields.Boolean('Includeopt-outlink',default=True)
    mailing_id=fields.Many2one('mailing.mailing',string='Mailing')
    utm_campaign_id=fields.Many2one('utm.campaign',string='Campaign')

    #------------------------------------------------------------
    #Massmodespecific
    #------------------------------------------------------------

    def_get_unsubscribe_url(self,res_id,trace_code,number):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        returnwerkzeug.urls.url_join(
            base_url,
            '/sms/%s/%s'%(self.mailing_id.id,trace_code)
        )

    def_prepare_mass_sms_trace_values(self,record,sms_values):
        trace_code=self.env['mailing.trace']._get_random_code()
        trace_values={
            'model':self.res_model,
            'res_id':record.id,
            'trace_type':'sms',
            'mass_mailing_id':self.mailing_id.id,
            'sms_number':sms_values['number'],
            'sms_code':trace_code,
        }
        ifsms_values['state']=='error':
            ifsms_values['error_code']=='sms_number_format':
                trace_values['sent']=fields.Datetime.now()
                trace_values['bounced']=fields.Datetime.now()
            else:
                trace_values['exception']=fields.Datetime.now()
        elifsms_values['state']=='canceled':
            trace_values['ignored']=fields.Datetime.now()
        else:
            ifself.mass_sms_allow_unsubscribe:
                sms_values['body']='%s\n%s'%(sms_values['body']or'',_('STOPSMS:%s',self._get_unsubscribe_url(record.id,trace_code,sms_values['number'])))
        returntrace_values

    def_get_blacklist_record_ids(self,records,recipients_info):
        """Consideropt-outedcontactasbeingblacklistedforthatspecific
        mailing."""
        res=super(SMSComposer,self)._get_blacklist_record_ids(records,recipients_info)
        ifself.mailing_id:
            optout_res_ids=self.mailing_id._get_opt_out_list_sms()
            res+=optout_res_ids
        returnres

    def_get_done_record_ids(self,records,recipients_info):
        """A/Btestingcouldleadtorecordshavingbeenalreadymailed."""
        res=super(SMSComposer,self)._get_done_record_ids(records,recipients_info)
        ifself.mailing_id:
            seen_ids,seen_list=self.mailing_id._get_seen_list_sms()
            res+=seen_ids
        returnres

    def_prepare_body_values(self,records):
        all_bodies=super(SMSComposer,self)._prepare_body_values(records)
        ifself.mailing_id:
            tracker_values=self.mailing_id._get_link_tracker_values()
            forsms_id,bodyinall_bodies.items():
                body=self.env['mail.render.mixin'].sudo()._shorten_links_text(body,tracker_values)
                all_bodies[sms_id]=body
        returnall_bodies

    def_prepare_mass_sms_values(self,records):
        result=super(SMSComposer,self)._prepare_mass_sms_values(records)
        ifself.composition_mode=='mass'andself.mailing_id:
            forrecordinrecords:
                sms_values=result[record.id]

                trace_values=self._prepare_mass_sms_trace_values(record,sms_values)
                sms_values.update({
                    'mailing_id':self.mailing_id.id,
                    'mailing_trace_ids':[(0,0,trace_values)],
                })
        returnresult

    def_prepare_mass_sms(self,records,sms_record_values):
        sms_all=super(SMSComposer,self)._prepare_mass_sms(records,sms_record_values)
        ifself.mailing_id:
            updated_bodies=sms_all._update_body_short_links()
            forsmsinsms_all:
                sms.body=updated_bodies[sms.id]
        returnsms_all
