#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
importwerkzeug.urls

fromflectraimportapi,fields,models,tools


classMailMail(models.Model):
    """Addthemassmailingcampaigndatatomail"""
    _inherit=['mail.mail']

    mailing_id=fields.Many2one('mailing.mailing',string='MassMailing')
    mailing_trace_ids=fields.One2many('mailing.trace','mail_mail_id',string='Statistics')

    @api.model_create_multi
    defcreate(self,values_list):
        """Overridemail_mailcreationtocreateanentryinmail.mail.statistics"""
        #TDEnote:shouldbeafter'allvaluescomputed',tohavevalues(FIXMEaftermergingotherbranchholdingcreaterefactoring)
        mails=super(MailMail,self).create(values_list)
        formail,valuesinzip(mails,values_list):
            ifvalues.get('mailing_trace_ids'):
                mail.mailing_trace_ids.write({'message_id':mail.message_id})
        returnmails

    def_get_tracking_url(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token=tools.hmac(self.env(su=True),'mass_mailing-mail_mail-open',self.id)
        returnwerkzeug.urls.url_join(base_url,'mail/track/%s/%s/blank.gif'%(self.id,token))

    def_send_prepare_body(self):
        """OverridetoaddthetrackingURLtothebodyandtoadd
        traceIDinshortenedurls"""
        #TDE:temporaryaddition(mailwasparameter)duetosemi-new-API
        self.ensure_one()
        body=super(MailMail,self)._send_prepare_body()

        ifself.mailing_idandbodyandself.mailing_trace_ids:
            formatchinre.findall(tools.URL_REGEX,self.body_html):
                href=match[0]
                url=match[1]

                parsed=werkzeug.urls.url_parse(url,scheme='http')

                ifparsed.scheme.startswith('http')andparsed.path.startswith('/r/'):
                    new_href=href.replace(url,url+'/m/'+str(self.mailing_trace_ids[0].id))
                    body=body.replace(href,new_href)

            #generatetrackingURL
            tracking_url=self._get_tracking_url()
            body=tools.append_content_to_html(
                body,
                '<imgsrc="%s"/>'%tracking_url,
                plaintext=False,
            )

        body=self.env['mail.render.mixin']._replace_local_links(body)

        returnbody

    def_send_prepare_values(self,partner=None):
        #TDE:temporaryaddition(mailwasparameter)duetosemi-new-API
        res=super(MailMail,self)._send_prepare_values(partner)
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
        ifself.mailing_idandres.get('body')andres.get('email_to'):
            emails=tools.email_split(res.get('email_to')[0])
            email_to=emailsandemails[0]orFalse

            urls_to_replace=[
               (base_url+'/unsubscribe_from_list',self.mailing_id._get_unsubscribe_url(email_to,self.res_id)),
               (base_url+'/view',self.mailing_id._get_view_url(email_to,self.res_id))
            ]

            forurl_to_replace,new_urlinurls_to_replace:
                ifurl_to_replaceinres['body']:
                    res['body']=res['body'].replace(url_to_replace,new_urlifnew_urlelse'#')
        returnres

    def_postprocess_sent_message(self,success_pids,failure_reason=False,failure_type=None):
        mail_sent=notfailure_type #weconsiderthatarecipienterrorisafailurewithmassmaillingandshowthemasfailed
        formailinself:
            ifmail.mailing_id:
                ifmail_sentisTrueandmail.mailing_trace_ids:
                    mail.mailing_trace_ids.write({'sent':fields.Datetime.now(),'exception':False})
                elifmail_sentisFalseandmail.mailing_trace_ids:
                    mail.mailing_trace_ids.write({'exception':fields.Datetime.now(),'failure_type':failure_type})
        returnsuper(MailMail,self)._postprocess_sent_message(success_pids,failure_reason=failure_reason,failure_type=failure_type)
