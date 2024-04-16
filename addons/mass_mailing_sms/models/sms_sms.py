#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportfields,models,tools


classSmsSms(models.Model):
    _inherit=['sms.sms']

    mailing_id=fields.Many2one('mailing.mailing',string='MassMailing')
    mailing_trace_ids=fields.One2many('mailing.trace','sms_sms_id',string='Statistics')

    def_update_body_short_links(self):
        """OverridetotweakshortenedURLsbyaddingstatisticsids,allowingto
        findcustomerbackonceclicked."""
        shortened_schema=self.env['ir.config_parameter'].sudo().get_param('web.base.url')+'/r/'
        res=dict.fromkeys(self.ids,False)
        forsmsinself:
            ifnotsms.mailing_idornotsms.body:
                res[sms.id]=sms.body
                continue

            body=sms.body
            forurlinre.findall(tools.TEXT_URL_REGEX,body):
                ifurl.startswith(shortened_schema):
                    body=body.replace(url,url+'/s/%s'%sms.id)
            res[sms.id]=body
        returnres

    def_postprocess_iap_sent_sms(self,iap_results,failure_reason=None,delete_all=False):
        all_sms_ids=[item['res_id']foriteminiap_results]
        ifany(sms.mailing_idforsmsinself.env['sms.sms'].sudo().browse(all_sms_ids)):
            forstateinself.IAP_TO_SMS_STATE.keys():
                sms_ids=[item['res_id']foriteminiap_resultsifitem['state']==state]
                traces=self.env['mailing.trace'].sudo().search([
                    ('sms_sms_id_int','in',sms_ids)
                ])
                iftracesandstate=='success':
                    traces.write({'sent':fields.Datetime.now(),'exception':False})
                eliftraces:
                    traces.set_failed(failure_type=self.IAP_TO_SMS_STATE[state])
        returnsuper(SmsSms,self)._postprocess_iap_sent_sms(iap_results,failure_reason=failure_reason,delete_all=delete_all)
