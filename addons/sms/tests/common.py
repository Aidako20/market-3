#-*-coding:utf-8-*-

fromcontextlibimportcontextmanager
fromunittest.mockimportpatch

fromflectraimportexceptions,tools
fromflectra.testsimportcommon
fromflectra.addons.mail.tests.commonimportMailCommon
fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.addons.sms.models.sms_apiimportSmsApi
fromflectra.addons.sms.models.sms_smsimportSmsSms


classMockSMS(common.BaseCase):

    deftearDown(self):
        super(MockSMS,self).tearDown()
        self._clear_sms_sent()

    @contextmanager
    defmockSMSGateway(self,sms_allow_unlink=False,sim_error=None,nbr_t_error=None):
        self._clear_sms_sent()
        sms_create_origin=SmsSms.create
        sms_unlink_origin=SmsSms.unlink

        def_contact_iap(local_endpoint,params):
            #mocksinglesmssending
            iflocal_endpoint=='/iap/message_send':
                self._sms+=[{
                    'number':number,
                    'body':params['message'],
                }fornumberinparams['numbers']]
                returnTrue #send_messagev0APIreturnsalwaysTrue
            #mockbatchsending
            iflocal_endpoint=='/iap/sms/2/send':
                result=[]
                forto_sendinparams['messages']:
                    res={'res_id':to_send['res_id'],'state':'success','credit':1}
                    error=sim_erroror(nbr_t_errorandnbr_t_error.get(to_send['number']))
                    iferroranderror=='credit':
                        res.update(credit=0,state='insufficient_credit')
                    eliferroranderror=='wrong_number_format':
                        res.update(state='wrong_number_format')
                    eliferroranderror=='unregistered':
                        res.update(state='unregistered')
                    eliferroranderror=='jsonrpc_exception':
                        raiseexceptions.AccessError(
                            'Theurlthatthisservicerequestedreturnedanerror.Pleasecontacttheauthoroftheapp.Theurlittriedtocontactwas'+local_endpoint
                        )
                    result.append(res)
                    ifres['state']=='success':
                        self._sms.append({
                            'number':to_send['number'],
                            'body':to_send['content'],
                        })
                returnresult

        def_sms_sms_create(model,*args,**kwargs):
            res=sms_create_origin(model,*args,**kwargs)
            self._new_sms+=res.sudo()
            returnres

        def_sms_sms_unlink(records,*args,**kwargs):
            ifsms_allow_unlink:
                returnsms_unlink_origin(records,*args,**kwargs)
            #hack:insteadofunlink,updatestatetosentfortests
            else:
                records.filtered(lambdasms:sms.idinself._new_sms.ids).state='sent'
            returnTrue

        try:
            withpatch.object(SmsApi,'_contact_iap',side_effect=_contact_iap),\
                    patch.object(SmsSms,'create',autospec=True,wraps=SmsSms,side_effect=_sms_sms_create),\
                    patch.object(SmsSms,'unlink',autospec=True,wraps=SmsSms,side_effect=_sms_sms_unlink):
                yield
        finally:
            pass

    def_clear_sms_sent(self):
        self._sms=[]
        self._new_sms=self.env['sms.sms'].sudo()

    def_clear_outoing_sms(self):
        """AsSMSgatewaymockkeepsSMS,wemayneedtoremovethemmanually
        ifthereareseveraltestsinthesametx."""
        self.env['sms.sms'].sudo().search([('state','=','outgoing')]).unlink()


classSMSCase(MockSMS):
    """MaintestclasstousewhentestingSMSintegrations.Containshelpersandtoolsrelated
    tonotificationsentbySMS."""

    def_find_sms_sent(self,partner,number):
        ifnumberisNoneandpartner:
            number=partner.phone_get_sanitized_number()
        sent_sms=next((smsforsmsinself._smsifsms['number']==number),None)
        ifnotsent_sms:
            raiseAssertionError('sentsmsnotfoundfor%s(number:%s)'%(partner,number))
        returnsent_sms

    def_find_sms_sms(self,partner,number,status):
        ifnumberisNoneandpartner:
            number=partner.phone_get_sanitized_number()
        domain=[('id','in',self._new_sms.ids),
                  ('partner_id','=',partner.id),
                  ('number','=',number)]
        ifstatus:
            domain+=[('state','=',status)]

        sms=self.env['sms.sms'].sudo().search(domain)
        ifnotsms:
            raiseAssertionError('sms.smsnotfoundfor%s(number:%s/status%s)'%(partner,number,status))
        iflen(sms)>1:
            raiseNotImplementedError()
        returnsms

    defassertNoSMS(self):
        """Checknosmswentthroughgatewayduringmock."""
        self.assertTrue(len(self._new_sms)==0)

    defassertSMSIapSent(self,numbers,content=None):
        """ChecksentSMS.Orderisnotchecked.Eachnumbershouldhavereceived
        thesamecontent.Usefultocheckbatchsending.

        :paramnumbers:listofnumbers;
        :paramcontent:contenttocheckforeachnumber;
        """
        fornumberinnumbers:
            sent_sms=next((smsforsmsinself._smsifsms['number']==number),None)
            self.assertTrue(bool(sent_sms),'Number%snotfoundin%s'%(number,repr([s['number']forsinself._sms])))
            ifcontentisnotNone:
                self.assertIn(content,sent_sms['body'])

    defassertSMSSent(self,numbers,content=None):
        """Deprecated.Removein14.4"""
        returnself.assertSMSIapSent(numbers,content=content)

    defassertSMS(self,partner,number,status,error_code=None,
                  content=None,fields_values=None):
        """Finda``sms.sms``record,basedongivenpartner,numberandstatus.

        :parampartner:optionalpartner,usedtofinda``sms.sms``andanumber
          ifnotgiven;
        :paramnumber:optionalnumber,usedtofinda``sms.sms``,notablyif
          partnerisnotgiven;
        :paramerror_code:checkerrorcodeifSMSisnotsentoroutgoing;
        :paramcontent:ifgiven,shouldbecontainedinsmsbody;
        :paramfields_values:optionalvaluesallowingtocheckdirectlysome
          valueson``sms.sms``record;
        """
        sms_sms=self._find_sms_sms(partner,number,status)
        iferror_code:
            self.assertEqual(sms_sms.error_code,error_code)
        ifcontentisnotNone:
            self.assertIn(content,sms_sms.body)
        forfname,fvaluein(fields_valuesor{}).items():
            self.assertEqual(
                sms_sms[fname],fvalue,
                'SMS:expected%sfor%s,got%s'%(fvalue,fname,sms_sms[fname]))
        ifstatus=='sent':
            self.assertSMSIapSent([sms_sms.number],content=content)

    defassertSMSCanceled(self,partner,number,error_code,content=None,fields_values=None):
        """CheckcanceledSMS.Searchisdoneforapairpartner/numberwhere
        partnercanbeanemptyrecordset."""
        self.assertSMS(partner,number,'canceled',error_code=error_code,content=content,fields_values=fields_values)

    defassertSMSFailed(self,partner,number,error_code,content=None,fields_values=None):
        """CheckfailedSMS.Searchisdoneforapairpartner/numberwhere
        partnercanbeanemptyrecordset."""
        self.assertSMS(partner,number,'error',error_code=error_code,content=content,fields_values=fields_values)

    defassertSMSOutgoing(self,partner,number,content=None,fields_values=None):
        """CheckoutgoingSMS.Searchisdoneforapairpartner/numberwhere
        partnercanbeanemptyrecordset."""
        self.assertSMS(partner,number,'outgoing',content=content,fields_values=fields_values)

    defassertNoSMSNotification(self,messages=None):
        base_domain=[('notification_type','=','sms')]
        ifmessagesisnotNone:
            base_domain+=[('mail_message_id','in',messages.ids)]
        self.assertEqual(self.env['mail.notification'].search(base_domain),self.env['mail.notification'])
        self.assertEqual(self._sms,[])

    defassertSMSNotification(self,recipients_info,content,messages=None,check_sms=True,sent_unlink=False):
        """Checkcontentofnotifications.

          :paramrecipients_info:list[{
            'partner':res.partnerrecord(maybeempty),
            'number':numberusedfornotification(maybeempty,computedbasedonpartner),
            'state':ready/sent/exception/canceled(sentbydefault),
            'failure_type':optional:sms_number_missing/sms_number_format/sms_credit/sms_server
            },{...}]
        """
        partners=self.env['res.partner'].concat(*list(p['partner']forpinrecipients_infoifp.get('partner')))
        numbers=[p['number']forpinrecipients_infoifp.get('number')]
        #specialcaseofvoidnotifications:checkforFalse/Falsenotifications
        ifnotpartnersandnotnumbers:
            numbers=[False]
        base_domain=[
            '|',('res_partner_id','in',partners.ids),
            '&',('res_partner_id','=',False),('sms_number','in',numbers),
            ('notification_type','=','sms')
        ]
        ifmessagesisnotNone:
            base_domain+=[('mail_message_id','in',messages.ids)]
        notifications=self.env['mail.notification'].search(base_domain)

        self.assertEqual(notifications.mapped('res_partner_id'),partners)

        forrecipient_infoinrecipients_info:
            partner=recipient_info.get('partner',self.env['res.partner'])
            number=recipient_info.get('number')
            state=recipient_info.get('state','sent')
            ifnumberisNoneandpartner:
                number=partner.phone_get_sanitized_number()

            notif=notifications.filtered(lambdan:n.res_partner_id==partnerandn.sms_number==numberandn.notification_status==state)
            self.assertTrue(notif,'SMS:notfoundnotificationfor%s(number:%s,state:%s)'%(partner,number,state))

            ifstatenotin('sent','ready','canceled'):
                self.assertEqual(notif.failure_type,recipient_info['failure_type'])
            ifcheck_sms:
                ifstate=='sent':
                    ifsent_unlink:
                        self.assertSMSIapSent([number],content=content)
                    else:
                        self.assertSMS(partner,number,'sent',content=content)
                elifstate=='ready':
                    self.assertSMS(partner,number,'outgoing',content=content)
                elifstate=='exception':
                    self.assertSMS(partner,number,'error',error_code=recipient_info['failure_type'],content=content)
                elifstate=='canceled':
                    self.assertSMS(partner,number,'canceled',error_code=recipient_info['failure_type'],content=content)
                else:
                    raiseNotImplementedError('Notimplemented')

        ifmessagesisnotNone:
            formessageinmessages:
                self.assertEqual(content,tools.html2plaintext(message.body).rstrip('\n'))

    defassertSMSLogged(self,records,body):
        forrecordinrecords:
            message=record.message_ids[-1]
            self.assertEqual(message.subtype_id,self.env.ref('mail.mt_note'))
            self.assertEqual(message.message_type,'sms')
            self.assertEqual(tools.html2plaintext(message.body).rstrip('\n'),body)


classSMSCommon(MailCommon,MockSMS):

    @classmethod
    defsetUpClass(cls):
        super(SMSCommon,cls).setUpClass()
        cls.user_employee.write({'login':'employee'})

        #updatecountrytobelgiuminordertotestsanitizationofnumbers
        cls.user_employee.company_id.write({'country_id':cls.env.ref('base.be').id})

        #somenumbersfortesting
        cls.random_numbers_str='+32456998877,0456665544'
        cls.random_numbers=cls.random_numbers_str.split(',')
        cls.random_numbers_san=[phone_validation.phone_format(number,'BE','32',force_format='E164')fornumberincls.random_numbers]
        cls.test_numbers=['+32456010203','0456040506','0032456070809']
        cls.test_numbers_san=[phone_validation.phone_format(number,'BE','32',force_format='E164')fornumberincls.test_numbers]

        #somenumbersformasstesting
        cls.mass_numbers=['04561%s2%s3%s'%(x,x,x)forxinrange(0,10)]
        cls.mass_numbers_san=[phone_validation.phone_format(number,'BE','32',force_format='E164')fornumberincls.mass_numbers]

    @classmethod
    def_create_sms_template(cls,model,body=False):
        returncls.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':cls.env['ir.model']._get(model).id,
            'body':bodyifbodyelse'Dear${object.display_name}thisisanSMS.'
        })
