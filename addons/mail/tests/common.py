#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importemail
importemail.policy
importtime

fromcollectionsimportdefaultdict
fromcontextlibimportcontextmanager
fromfunctoolsimportpartial
fromlxmlimporthtml
fromunittest.mockimportpatch
fromsmtplibimportSMTPServerDisconnected

fromflectraimportexceptions
fromflectra.addons.base.models.ir_mail_serverimportIrMailServer,MailDeliveryException
fromflectra.addons.bus.models.busimportImBus,json_dump
fromflectra.addons.mail.models.mail_mailimportMailMail
fromflectra.addons.mail.models.mail_messageimportMessage
fromflectra.addons.mail.models.mail_notificationimportMailNotification
fromflectra.testsimportcommon,new_test_user
fromflectra.toolsimportformataddr,pycompat

mail_new_test_user=partial(new_test_user,context={'mail_create_nolog':True,'mail_create_nosubscribe':True,'mail_notrack':True,'no_reset_password':True})


classMockEmail(common.BaseCase):
    """Tools,helpersandassertsformailgateway-relatedtests

    Usefulreminders
        Mailstate:('outgoing','Outgoing'),('sent','Sent'),
                    ('received','Received'),('exception','DeliveryFailed'),
                    ('cancel','Cancelled')
    """

    #------------------------------------------------------------
    #GATEWAYMOCK
    #------------------------------------------------------------

    @contextmanager
    defmock_mail_gateway(self,mail_unlink_sent=False,sim_error=None):
        build_email_origin=IrMailServer.build_email
        mail_create_origin=MailMail.create
        mail_unlink_origin=MailMail.unlink
        self.mail_unlink_sent=mail_unlink_sent
        self._init_mail_mock()

        def_ir_mail_server_connect(model,*args,**kwargs):
            ifsim_errorandsim_error=='connect_smtp_notfound':
                raiseexceptions.UserError(
                    "MissingSMTPServer\nPleasedefineatleastoneSMTPserver,orprovidetheSMTPparametersexplicitly.")
            ifsim_errorandsim_error=='connect_failure':
                raiseException("Someexception")
            returnNone

        def_ir_mail_server_build_email(model,*args,**kwargs):
            self._mails.append(kwargs)
            self._mails_args.append(args)
            returnbuild_email_origin(model,*args,**kwargs)

        def_ir_mail_server_send_email(model,message,*args,**kwargs):
            if'@'notinmessage['To']:
                raiseAssertionError(model.NO_VALID_RECIPIENT)
            ifsim_errorandsim_error=='send_assert':
                raiseAssertionError('AssertionError')
            elifsim_errorandsim_error=='send_disconnect':
                raiseSMTPServerDisconnected('SMTPServerDisconnected')
            elifsim_errorandsim_error=='send_delivery':
                raiseMailDeliveryException('MailDeliveryException')
            returnmessage['Message-Id']

        def_mail_mail_create(model,*args,**kwargs):
            res=mail_create_origin(model,*args,**kwargs)
            self._new_mails+=res.sudo()
            returnres

        def_mail_mail_unlink(model,*args,**kwargs):
            ifself.mail_unlink_sent:
                returnmail_unlink_origin(model,*args,**kwargs)
            returnTrue

        withpatch.object(IrMailServer,'connect',autospec=True,wraps=IrMailServer,side_effect=_ir_mail_server_connect)asir_mail_server_connect_mock,\
                patch.object(IrMailServer,'build_email',autospec=True,wraps=IrMailServer,side_effect=_ir_mail_server_build_email)asir_mail_server_build_email_mock,\
                patch.object(IrMailServer,'send_email',autospec=True,wraps=IrMailServer,side_effect=_ir_mail_server_send_email)asir_mail_server_send_email_mock,\
                patch.object(MailMail,'create',autospec=True,wraps=MailMail,side_effect=_mail_mail_create)as_mail_mail_create_mock,\
                patch.object(MailMail,'unlink',autospec=True,wraps=MailMail,side_effect=_mail_mail_unlink)asmail_mail_unlink_mock:
            yield

    def_init_mail_mock(self):
        self._mails=[]
        self._mails_args=[]
        self._new_mails=self.env['mail.mail'].sudo()

    #------------------------------------------------------------
    #GATEWAYTOOLS
    #------------------------------------------------------------

    @classmethod
    def_init_mail_gateway(cls):
        cls.alias_domain='test.com'
        cls.alias_catchall='catchall.test'
        cls.alias_bounce='bounce.test'
        cls.env['ir.config_parameter'].set_param('mail.bounce.alias',cls.alias_bounce)
        cls.env['ir.config_parameter'].set_param('mail.catchall.domain',cls.alias_domain)
        cls.env['ir.config_parameter'].set_param('mail.catchall.alias',cls.alias_catchall)
        cls.mailer_daemon_email=formataddr(('MAILER-DAEMON','%s@%s'%(cls.alias_bounce,cls.alias_domain)))

    defformat(self,template,to='groups@example.com,other@gmail.com',subject='Frogs',
               email_from='SylvieLelitre<test.sylvie.lelitre@agrolait.com>',return_path='',cc='',
               extra='',msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
               **kwargs):
        returntemplate.format(
            subject=subject,to=to,cc=cc,
            email_from=email_from,return_path=return_path,
            extra=extra,msg_id=msg_id,
            **kwargs)

    defformat_and_process(self,template,email_from,to,subject='Frogs',cc='',
                           return_path='',extra='', msg_id=False,
                           model=None,target_model='mail.test.gateway',target_field='name',
                           **kwargs):
        self.assertFalse(self.env[target_model].search([(target_field,'=',subject)]))
        ifnotmsg_id:
            msg_id="<%.7f-test@iron.sky>"%(time.time())

        mail=self.format(template,to=to,subject=subject,cc=cc,
                           return_path=return_path,extra=extra,
                           email_from=email_from,msg_id=msg_id,
                           **kwargs)
        self.env['mail.thread'].with_context(mail_channel_noautofollow=True).message_process(model,mail)
        returnself.env[target_model].search([(target_field,'=',subject)])

    defgateway_reply_wrecord(self,template,record,use_in_reply_to=True):
        """Deprecated,removein14.4"""
        returnself.gateway_mail_reply_wrecord(template,record,use_in_reply_to=use_in_reply_to)

    defgateway_mail_reply_wrecord(self,template,record,use_in_reply_to=True,
                                   target_model=None,target_field=None):
        """Simulateareplythroughthemailgateway.Usage:givingarecord,
        findanemailsenttohimanduseitsmessage-IDtosimulateareply.

        SomenoiseisaddedinReferencesjusttotestsomerobustness."""
        mail_mail=self._find_mail_mail_wrecord(record)

        ifuse_in_reply_to:
            extra='In-Reply-To:\r\n\t%s\n'%mail_mail.message_id
        else:
            disturbing_other_msg_id='<123456.654321@another.host.com>'
            extra='References:\r\n\t%s\n\r%s'%(mail_mail.message_id,disturbing_other_msg_id)

        returnself.format_and_process(
            template,
            mail_mail.email_to,
            mail_mail.reply_to,
            subject='Re:%s'%mail_mail.subject,
            extra=extra,
            msg_id='<123456.%s.%d@test.example.com>'%(record._name,record.id),
            target_model=target_modelorrecord._name,
            target_field=target_fieldorrecord._rec_name,
        )

    defgateway_mail_reply_wemail(self,template,email_to,use_in_reply_to=True,
                                  target_model=None,target_field=None):
        """Simulateareplythroughthemailgateway.Usage:givingarecord,
        findanemailsenttohimanduseitsmessage-IDtosimulateareply.

        SomenoiseisaddedinReferencesjusttotestsomerobustness."""
        sent_mail=self._find_sent_mail_wemail(email_to)

        ifuse_in_reply_to:
            extra='In-Reply-To:\r\n\t%s\n'%sent_mail['message_id']
        else:
            disturbing_other_msg_id='<123456.654321@another.host.com>'
            extra='References:\r\n\t%s\n\r%s'%(sent_mail['message_id'],disturbing_other_msg_id)

        returnself.format_and_process(
            template,
            sent_mail['email_to'],
            sent_mail['reply_to'],
            subject='Re:%s'%sent_mail['subject'],
            extra=extra,
            target_model=target_model,
            target_field=target_fieldor'name',
        )

    deffrom_string(self,text):
        returnemail.message_from_string(pycompat.to_text(text),policy=email.policy.SMTP)

    defassertHtmlEqual(self,value,expected,message=None):
        tree=html.fragment_fromstring(value,parser=html.HTMLParser(encoding='utf-8'),create_parent='body')

        #massmailing:addbasetagwehavetoremove
        forbase_nodeintree.xpath('//base'):
            base_node.getparent().remove(base_node)

        #chatter:readmore/readlessTODO

        #massmailing:addbasetagwehavetoremove
        expected_node=html.fragment_fromstring(expected,create_parent='body')

        ifmessage:
            self.assertEqual(tree,expected_node,message)
        else:
            self.assertEqual(tree,expected_node)

    #------------------------------------------------------------
    #GATEWAYGETTERS
    #------------------------------------------------------------

    def_find_sent_mail_wemail(self,email_to):
        """Findasentemailwithagivenlistofrecipients.Emailshouldmatch
        exactlytherecipients.

        :paramemail-to:alistofemailsthatwillbecomparedtoemail_to
          ofsentemails(alsoalistofemails);

        :returnemail:anemailwhichisadictionarymappingvaluesgivento
          ``build_email``;
        """
        forsent_emailinself._mails:
            ifset(sent_email['email_to'])==set([email_to]):
                break
        else:
            raiseAssertionError('sentmailnotfoundforemail_to%s'%(email_to))
        returnsent_email

    def_filter_mail(self,status=None,mail_message=None,author=None,email_from=None):
        """Filtermailgeneratedduringmock,basedoncommonparameters

        :paramstatus:stateofmail.mail.Ifnotvoiduseittofiltermail.mail
          record;
        :parammail_message:optionalcheck/filteronmail_message_idfieldaka
          a``mail.message``record;
        :paramauthor:optionalcheck/filteronauthor_idfieldakaa``res.partner``
          record;
        :paramemail_from:optionalcheck/filteronemail_fromfield(maydifferfrom
          author,usednotablyincaseofconcurrentmailingstodistinguishemails);
        """
        filtered=self._new_mails.env['mail.mail']
        formailinself._new_mails:
            ifstatusisnotNoneandmail.state!=status:
                continue
            ifmail_messageisnotNoneandmail.mail_message_id!=mail_message:
                continue
            ifauthorisnotNoneandmail.author_id!=author:
                continue
            ifemail_fromisnotNoneandmail.email_from!=email_from:
                continue
            filtered+=mail
        returnfiltered

    def_find_mail_mail_wid(self,mail_id,status=None,mail_message=None,author=None,email_from=None):
        """Finda``mail.mail``recordbasedonagivenID(usednotablywhenhaving
        mailIDinmailingtraces).

        :returnmail:a``mail.mail``recordgeneratedduringthemockandmatching
          givenID;
        """
        filtered=self._filter_mail(status=status,mail_message=mail_message,author=author,email_from=email_from)
        formailinfiltered:
            ifmail.id==mail_id:
                break
        else:
            debug_info='\n'.join(
                f'From:{mail.author_id}({mail.email_from})-ID{mail.id}(State:{mail.state})'
                formailinself._new_mails
            )
            raiseAssertionError(
                f'mail.mailnotfoundforID{mail_id}/message{mail_message}/status{status}/author{author}\n{debug_info}'
            )
        returnmail

    def_find_mail_mail_wpartners(self,recipients,status,mail_message=None,author=None,email_from=None):
        """Findamail.mailrecordbasedonvariousparameters,notablyalist
        ofrecipients(partners).

        :paramrecipients:a``res.partner``recordsetCheckallofthemareinmail
          recipientstofindtherightmail.mailrecord;

        :returnmail:a``mail.mail``recordgeneratedduringthemockandmatching
          givenparametersandfilters;
        """
        filtered=self._filter_mail(status=status,mail_message=mail_message,author=author,email_from=email_from)
        formailinfiltered:
            ifall(pinmail.recipient_idsforpinrecipients):
                break
        else:
            debug_info='\n'.join(
                f'From:{mail.author_id}({mail.email_from})-To:{sorted(mail.recipient_ids.ids)}(State:{mail.state})'
                formailinself._new_mails
            )
            recipients_info=f'Missing:{[r.nameforrinrecipientsifr.idnotinfiltered.recipient_ids.ids]}'
            raiseAssertionError(
                f'mail.mailnotfoundformessage{mail_message}/status{status}/recipients{sorted(recipients.ids)}/author{author}\n{recipients_info}\n{debug_info}'
            )
        returnmail

    def_find_mail_mail_wemail(self,email_to,status,mail_message=None,author=None,email_from=None):
        """Findamail.mailrecordbasedonvariousparameters,notablyalist
        ofemailto(stringemails).

        :paramemail_to:eithermatchingmail.email_tovalue,eitheramailsent
          toasinglerecipientwhoseemailisemail_to;

        :returnmail:a``mail.mail``recordgeneratedduringthemockandmatching
          givenparametersandfilters;
        """
        filtered=self._filter_mail(status=status,mail_message=mail_message,author=author,email_from=email_from)
        formailinfiltered:
            if(mail.email_to==email_toandnotmail.recipient_ids)or(notmail.email_toandmail.recipient_ids.email==email_to):
                break
        else:
            debug_info='\n'.join(
                f'From:{mail.author_id}({mail.email_from})-To:{mail.email_to}/{sorted(mail.recipient_ids.mapped("email"))}(State:{mail.state})'
                formailinself._new_mails
            )
            raiseAssertionError(
                f'mail.mailnotfoundformessage{mail_message}/status{status}/email_to{email_to}/author{author}\n{debug_info}'
            )
        returnmail

    def_find_mail_mail_wrecord(self,record,status=None,mail_message=None,author=None,email_from=None):
        """Findamail.mailrecordbasedonmodel/res_idofarecord.

        :returnmail:a``mail.mail``recordgeneratedduringthemock;
        """
        filtered=self._filter_mail(status=status,mail_message=mail_message,author=author,email_from=email_from)
        formailinfiltered:
            ifmail.model==record._nameandmail.res_id==record.id:
                break
        else:
            debug_info='\n'.join(
                f'From:{mail.author_id}({mail.email_from})-Model{mail.model}/ResId{mail.res_id}(State:{mail.state})'
                formailinself._new_mails
            )
            raiseAssertionError(
                f'mail.mailnotfoundformessage{mail_message}/status{status}/record{record.model},{record.id}/author{author}\n{debug_info}'
            )
        returnmail

    def_find_sent_email(self,email_from,emails_to,subject=None):
        """Findanoutgoingemailbasedonfrom/toandoptionalsubjectwhen
        havingaconflict.

        :returnsent_email:anoutgoingemailgeneratedduringthemock;
        """
        sent_emails=[
            mailformailinself._mails
            ifset(mail['email_to'])==set(emails_to)andmail['email_from']==email_from
        ]
        iflen(sent_emails)>1andsubject:
            #trytobetterfilter
            sent_email=next((mailformailinsent_emailsifmail['subject']==subject),False)
        else:
            sent_email=sent_emails[0]ifsent_emailselseFalse
        returnsent_email

    #------------------------------------------------------------
    #GATEWAYASSERTS
    #------------------------------------------------------------

    def_assertMailMail(self,mail,recipients_list,status,
                        email_to_recipients=None,author=None,
                        content=None,fields_values=None,email_values=None):
        """Assertmail.mailrecordvaluesandmayberelatedemails.Allow
        assertingtheircontent.Recordstocheckaretheonegeneratedwhen
        usingmock(mail.mailandoutgoingemails).

        :parammail:a``mail.mail``record;
        :paramrecipients_list:an``res.partner``recordsetoralistof
          emails(botharesupported,see``_find_mail_mail_wpartners``and
          ``_find_mail_mail_wemail``);
        :paramstatus:mail.mailstateusedtofiltermails.If``sent``thismethod
          alsocheckthatemailshavebeensenttroughgateway;
        :paramemail_to_recipients:usedforassertSentEmailtofindemailbased
          on'email_to'whendoingthematchdirectlybasedonrecipients_list
          beingpartnersitnoseasy(e.g.multiemails,...);
        :paramauthor:see``_find_mail_mail_wpartners``;
        :paramcontent:ifgiven,checkitiscontainedwithinmailhtmlbody;
        :paramfields_values:ifgiven,shouldbeadictionaryoffieldnames/
          valuesallowingtocheck``mail.mail``additionalvalues(subject,
          reply_to,...);
        :paramemail_values:ifgiven,shouldbeadictionaryofkeys/values
          allowingtochecksentemailadditionalvalues(ifany).
          See``assertSentEmail``;

        :paramcheck_mail_mail:deprecated,use``assertSentEmail``ifFalse
        """
        self.assertTrue(bool(mail))
        ifcontent:
            self.assertIn(content,mail.body_html)
        forfname,fvaluein(fields_valuesor{}).items():
            withself.subTest(fname=fname,fvalue=fvalue):
                self.assertEqual(
                    mail[fname],fvalue,
                    'Mail:expected%sfor%s,got%s'%(fvalue,fname,mail[fname])
                )
        ifstatus=='sent':
            ifemail_to_recipients:
                recipients=email_to_recipients #alreadyformatted
            else:
                recipients=[[r]forrinrecipients_list] #onepartner->listofasingleemail
            forrecipientinrecipients:
                withself.subTest(recipient=recipient):
                    self.assertSentEmail(
                        email_values['email_from']ifemail_valuesandemail_values.get('email_from')elseauthor,
                        recipient,
                        **(email_valuesor{})
                    )

    defassertMailMail(self,recipients,status,
                       email_to_recipients=None,
                       check_mail_mail=True,mail_message=None,author=None,
                       content=None,fields_values=None,email_values=None):
        """Assertmail.mailrecordsarecreatedandmaybesentasemails.This
        methodtakespartnersassourcetofindmailsandchecktheircontent.
        See'_assertMailMail'formoredetails.

        :paramrecipients:a``res.partner``recordset.See
          ``_find_mail_mail_wpartners``;
        :parammail_message:usedtofindtherelatedemail;

        See'_assertMailMail'formoredetailsaboutotherparameters.
        """
        found_mail=self._find_mail_mail_wpartners(recipients,status,mail_message=mail_message,author=author)
        self.assertTrue(bool(found_mail))
        self._assertMailMail(
            found_mail,recipients,status,
            email_to_recipients=email_to_recipients,
            author=author,content=content,
            fields_values=fields_values,email_values=email_values,
        )
        returnfound_mail

    defassertMailMailWEmails(self,emails,status,
                              email_to_recipients=None,
                              mail_message=None,author=None,
                              content=None,fields_values=None,email_values=None):
        """Assertmail.mailrecordsarecreatedandmaybesentasemails.This
        methodtakesemailsassourcetofindmailsandchecktheircontent.
        See'_assertMailMail'formoredetails.

        :paramemails:alistofemails.See``_find_mail_mail_wemail``;
        :parammail_message:usedtofindtherelatedemail;

        See'_assertMailMail'formoredetailsaboutotherparameters.
        """
        found_mail=False
        foremail_toinemails:
            found_mail=self._find_mail_mail_wemail(
                email_to,status,mail_message=mail_message,
                author=author,email_from=fields_values.get('email_from')
            )
            self.assertTrue(bool(found_mail))
            self._assertMailMail(
                found_mail,[email_to],status,
                email_to_recipients=email_to_recipients,
                author=author,content=content,
                fields_values=fields_values,email_values=email_values,
            )
        returnfound_mail

    defassertMailMailWRecord(self,record,recipients,status,
                              email_to_recipients=None,
                              mail_message=None,author=None,
                              content=None,fields_values=None,email_values=None):
        """Assertmail.mailrecordsarecreatedandmaybesentasemails. This
        methodtakesarecordassourcetofindmailsandchecktheircontent
        usingmodel/res_id.See'_assertMailMail'formoredetails.

        :paramrecord:arecordusedtofindemailssentrelatedonit.
          See``_find_mail_mail_wrecord``;
        :parammail_message:usedtofindtherelatedemail;

        See'_assertMailMail'formoredetailsaboutotherparameters.
        """
        found_mail=self._find_mail_mail_wrecord(record,mail_message=mail_message,author=author)
        self.assertTrue(bool(found_mail))
        self._assertMailMail(
            found_mail,recipients,status,
            email_to_recipients=email_to_recipients,
            author=author,content=content,
            fields_values=fields_values,email_values=email_values,
        )
        returnfound_mail

    defassertMailMailWId(self,mail_id,status,
                          email_to_recipients=None,
                          author=None,
                          content=None,fields_values=None):
        """Assertmail.mailrecordsarecreatedandmaybesentasemails.Allow
        assertingtheircontent.Recordstocheckaretheonegeneratedwhen
        usingmock(mail.mailandoutgoingemails).Thismethodtakespartners
        assourceofrecordfetchandassert.

        :parammail_id:a``mail.mail``DBID.See``_find_mail_mail_wid``;

        Forotherparameters,see``_assertMailMail``.
        """
        found_mail=self._find_mail_mail_wid(mail_id)
        self.assertTrue(bool(found_mail))
        self._assertMailMail(
            found_mail,[], #generallyusedwhenrecipientsareFalsy
            status,
            email_to_recipients=email_to_recipients,
            author=author,content=content,
            fields_values=fields_values,
        )
        returnfound_mail

    defassertNoMail(self,recipients,mail_message=None,author=None):
        """Checknomail.mailandemailwasgeneratedduringgatewaymock."""
        try:
            self._find_mail_mail_wpartners(recipients,False,mail_message=mail_message,author=author)
        exceptAssertionError:
            pass
        else:
            raiseAssertionError('mail.mailexistsformessage%s/recipients%sbutshouldnotexist'%(mail_message,recipients.ids))
        finally:
            self.assertNotSentEmail(recipients)

    defassertNotSentEmail(self,recipients=None):
        """Checknoemailwasgeneratedduringgatewaymock.

        :paramrecipients:
            Listofpartnerforwhichwewillcheckthatnoemailhavebeensent
            Orlistofemailaddress
            IfNone,wewillcheckthatnoemailatallhavebeensent
        """
        ifrecipientsisNone:
            mails=self._mails
        else:
            all_emails=[
                email_to.emailifisinstance(email_to,self.env['res.partner'].__class__)
                elseemail_to
                foremail_toinrecipients
            ]

            mails=[
                mail
                formailinself._mails
                ifany(emailinall_emailsforemailinmail['email_to'])
            ]

        self.assertEqual(len(mails),0)

    defassertSentEmail(self,author,recipients,**values):
        """Toolmethodtoeasethecheckofsendemails.

        :paramauthor:emailauthor,eitherastring(email),eitherapartner
          record;
        :paramrecipients:listofrecipients,eachbeingeitherastring(email),
          eitherapartnerrecord;
        :paramvalues:dictionaryofadditionalvaluestocheckemailcontent;
        """
        direct_check=['attachments','body_alternative','email_from','references','reply_to','subject']
        content_check=['body_alternative_content','body_content','references_content']
        other_check=['body','attachments_info','email_to']

        expected={}
        forfnameindirect_check+content_check+other_check:
            iffnameinvalues:
                expected[fname]=values[fname]
        unknown=set(values.keys())-set(direct_check+content_check+other_check)
        ifunknown:
            raiseNotImplementedError('Unsupported%s'%','.join(unknown))

        ifisinstance(author,self.env['res.partner'].__class__):
            expected['email_from']=formataddr((author.name,author.email))
        else:
            expected['email_from']=author

        if'email_to'invalues:
            email_to_list=values['email_to']
        else:
            email_to_list=[]
            foremail_toinrecipients:
                ifisinstance(email_to,self.env['res.partner'].__class__):
                    email_to_list.append(formataddr((email_to.name,email_to.emailor'False')))
                else:
                    email_to_list.append(email_to)
        expected['email_to']=email_to_list

        #fetchmail
        sent_mail=self._find_sent_email(
            expected['email_from'],
            expected['email_to'],
            values.get('subject'),
        )
        debug_info=''
        ifnotsent_mail:
            debug_info='-'.join('From:%s-To:%s'%(mail['email_from'],mail['email_to'])formailinself._mails)
        self.assertTrue(
            bool(sent_mail),
            'Expectedmailfrom%sto%snotfoundin%s'%(expected['email_from'],expected['email_to'],debug_info)
        )

        forvalindirect_check:
            ifvalinexpected:
                self.assertEqual(expected[val],sent_mail[val],'Valuefor%s:expected%s,received%s'%(val,expected[val],sent_mail[val]))
        if'attachments_info'inexpected:
            attachments=sent_mail['attachments']
            forattachment_infoinexpected['attachments_info']:
                attachment=next((attachforattachinattachmentsifattach[0]==attachment_info['name']),False)
                self.assertTrue(
                    bool(attachment),
                    f'Attachment{attachment_info["name"]}notfoundinattachments',
                )
                ifattachment_info.get('raw'):
                    self.assertEqual(attachment[1],attachment_info['raw'])
                ifattachment_info.get('type'):
                    self.assertEqual(attachment[2],attachment_info['type'])
            self.assertEqual(len(expected['attachments_info']),len(attachments))
        if'body'inexpected:
            self.assertHtmlEqual(expected['body'],sent_mail['body'],'Valuefor%s:expected%s,received%s'%('body',expected['body'],sent_mail['body']))
        forvalincontent_check:
            ifvalinexpected:
                self.assertIn(expected[val],sent_mail[val[:-8]],'Valuefor%s:%sdoesnotcontain%s'%(val,sent_mail[val[:-8]],expected[val]))

        returnsent_mail


classMailCase(MockEmail):
    """Tools,helpersandassertsformail-relatedtests,includingmail
    gatewaymockandhelpers(see´´MockEmail´´).

    Usefulreminders
        Notiftype: ('inbox','Inbox'),('email','Email')
        Notifstatus:('ready','ReadytoSend'),('sent','Sent'),
                      ('bounce','Bounced'),('exception','Exception'),
                      ('canceled','Canceled')
        Notiffailuretype:("SMTP","Connectionfailed(outgoingmailserverproblem)"),
                            ("RECIPIENT","Invalidemailaddress"),
                            ("BOUNCE","Emailaddressrejectedbydestination"),
                            ("UNKNOWN","Unknownerror")
    """
    _test_context={
        'mail_create_nolog':True,
        'mail_create_nosubscribe':True,
        'mail_notrack':True,
        'no_reset_password':True
    }

    @classmethod
    def_reset_mail_context(cls,record):
        returnrecord.with_context(
            mail_create_nolog=False,
            mail_create_nosubscribe=False,
            mail_notrack=False
        )

    defflush_tracking(self):
        """Forcethecreationoftrackingvalues."""
        self.env['base'].flush()
        self.cr.precommit.run()

    #------------------------------------------------------------
    #MAILMOCKS
    #------------------------------------------------------------

    @contextmanager
    defmock_bus(self):
        bus_bus_create_origin=ImBus.create
        self._init_mock_bus()

        def_bus_bus_create(model,*args,**kwargs):
            res=bus_bus_create_origin(model,*args,**kwargs)
            self._new_bus_notifs+=res.sudo()
            returnres

        withpatch.object(ImBus,'create',autospec=True,wraps=ImBus,side_effect=_bus_bus_create)as_bus_bus_create_mock:
            yield

    def_init_mock_bus(self):
        self._new_bus_notifs=self.env['bus.bus'].sudo()

    def_reset_bus(self):
        self.env['bus.bus'].sudo().search([]).unlink()

    @contextmanager
    defmock_mail_app(self):
        message_create_origin=Message.create
        notification_create_origin=MailNotification.create
        self._init_mock_mail()

        def_mail_message_create(model,*args,**kwargs):
            res=message_create_origin(model,*args,**kwargs)
            self._new_msgs+=res.sudo()
            returnres

        def_mail_notification_create(model,*args,**kwargs):
            res=notification_create_origin(model,*args,**kwargs)
            self._new_notifs+=res.sudo()
            returnres

        withpatch.object(Message,'create',autospec=True,wraps=Message,side_effect=_mail_message_create)as_mail_message_create_mock,\
                patch.object(MailNotification,'create',autospec=True,wraps=MailNotification,side_effect=_mail_notification_create)as_mail_notification_create_mock:
            yield

    def_init_mock_mail(self):
        self._new_msgs=self.env['mail.message'].sudo()
        self._new_notifs=self.env['mail.notification'].sudo()

    #------------------------------------------------------------
    #MAILTOOLS
    #------------------------------------------------------------

    @classmethod
    def_add_messages(cls,record,body_content,count=1,author=None,**kwargs):
        """Helper:add#countmessagesinrecordhistory"""
        author=authorifauthorelsecls.env.user.partner_id
        if'email_from'notinkwargs:
            kwargs['email_from']=author.email_formatted
        subtype_id=kwargs.get('subtype_id',cls.env.ref('mail.mt_comment').id)

        values={
            'model':record._name,
            'res_id':record.id,
            'author_id':author.id,
            'subtype_id':subtype_id,
        }
        values.update(kwargs)

        create_vals=[dict(
            values,body='%s/%02d'%(body_content,counter))
            forcounterinrange(count)]

        returncls.env['mail.message'].sudo().create(create_vals)

    @classmethod
    def_create_template(cls,model,template_values=None):
        create_values={
            'name':'TestTemplate',
            'subject':'About${object.name}',
            'body_html':'<p>Hello${object.name}</p>',
            'model_id':cls.env['ir.model']._get(model).id,
        }
        iftemplate_values:
            create_values.update(template_values)
        cls.email_template=cls.env['mail.template'].create(create_values)
        returncls.email_template


    def_generate_notify_recipients(self,partners):
        """Toolmethodtogeneraterecipientsdataaccordingtostructureused
        innotificationmethods.Purposeistoallowtestingofinternalsof
        somenotificationmethods,notablytestinglinksorgroup-basednotification
        details.

        Seenotably``MailThread._notify_compute_recipients()``.
        """
        return[
            {'id':partner.id,
             'active':True,
             'share':partner.partner_share,
             'groups':partner.user_ids.groups_id.ids,
             'notif':partner.user_ids.notification_typeor'email',
             'type':'user'ifpartner.user_idsandnotpartner.partner_shareelsepartner.user_idsand'portal'or'customer',
            }forpartnerinpartners
        ]

    #------------------------------------------------------------
    #MAILASSERTSWRAPPERS
    #------------------------------------------------------------

    @contextmanager
    defassertSinglePostNotifications(self,recipients_info,message_info=None,mail_unlink_sent=False,sim_error=None):
        """ShortcuttoassertMsgNotificationswhenhavingasinglemessagetocheck."""
        r_info=dict(message_infoifmessage_infoelse{})
        r_info.setdefault('content','')
        r_info['notif']=recipients_info
        withself.assertPostNotifications([r_info],mail_unlink_sent=mail_unlink_sent,sim_error=sim_error):
            yield

    @contextmanager
    defassertPostNotifications(self,recipients_info,mail_unlink_sent=False,sim_error=None):
        """Checkcontentofnotifications."""
        try:
            withself.mock_mail_gateway(mail_unlink_sent=mail_unlink_sent,sim_error=sim_error),self.mock_bus(),self.mock_mail_app():
                yield
        finally:
            done_msgs,done_notifs=self.assertMailNotifications(self._new_msgs,recipients_info)
            self.assertEqual(self._new_msgs,done_msgs,'Mail:invalidmessagecreation(%s)/expected(%s)'%(len(self._new_msgs),len(done_msgs)))
            self.assertEqual(self._new_notifs,done_notifs,'Mail:invalidnotificationcreation(%s)/expected(%s)'%(len(self._new_notifs),len(done_notifs)))

    @contextmanager
    defassertBus(self,channels,message_items=None):
        """Checkcontentofbusnotifications."""
        try:
            withself.mock_bus():
                yield
        finally:
            found_bus_notifs=self.assertBusNotifications(channels,message_items=message_items)
            self.assertEqual(self._new_bus_notifs,found_bus_notifs)

    @contextmanager
    defassertNoNotifications(self):
        try:
            withself.mock_mail_gateway(mail_unlink_sent=False,sim_error=None),self.mock_bus(),self.mock_mail_app():
                yield
        finally:
            self.assertFalse(bool(self._new_msgs))
            self.assertFalse(bool(self._new_notifs))

    #------------------------------------------------------------
    #MAILMODELSASSERTS
    #------------------------------------------------------------

    defassertMailNotifications(self,messages,recipients_info):
        """Checkbusnotificationscontent.Mandatoryandbasiccheckisabout
        channelsbeingnotified.Contentcheckisoptional.

        GNERATEDINPUT
        :parammessages:generatedmessagestocheck;

        EXPECTED
        :paramrecipients_info:listofdatadict:[
          {'content':messagecontent,
           'message_type':message_type(default:'comment'),
           'subtype':xmlidofmessagesubtype(default:'mail.mt_comment'),
           'notif':listofnotifiedrecipients:[
             {'partner':res.partnerrecord(maybeempty),
              'email':NOTSUPPORTEDYET,
              'status':notification_statustocheck,
              'type':notification_typetocheck,
              'is_read':is_readtocheck,
              'check_send':whetheroutgoingstuffhastobechecked;
              'failure_type':optional:oneoffailure_typekey
             },{...}]
          },{...}]

        PARAMETERS
        :paramunlink_sent:toknowwhethertocompute
        """
        partners=self.env['res.partner'].sudo().concat(*list(p['partner']foriinrecipients_infoforpini['notif']ifp.get('partner')))
        base_domain=[('res_partner_id','in',partners.ids)]
        ifmessagesisnotNone:
            base_domain+=[('mail_message_id','in',messages.ids)]
        notifications=self.env['mail.notification'].sudo().search(base_domain)

        done_msgs=self.env['mail.message'].sudo()
        done_notifs=self.env['mail.notification'].sudo()

        formessage_infoinrecipients_info:
            mbody,mtype=message_info.get('content',''),message_info.get('message_type','comment')
            msubtype=self.env.ref(message_info.get('subtype','mail.mt_comment'))

            #findmessage
            ifmessages:
                message=messages.filtered(lambdamessage:mbodyinmessage.bodyandmessage.message_type==mtypeandmessage.subtype_id==msubtype)
            else:
                message=self.env['mail.message'].sudo().search([('body','ilike',mbody),('message_type','=',mtype),('subtype_id','=',msubtype.id)],limit=1,order='idDESC')
            self.assertTrue(message,'Mail:notfoundmessage(content:%s,message_type:%s,subtype:%s)'%(mbody,mtype,msubtype.name))

            #checknotificationsandprepareassertdata
            email_groups=defaultdict(list)
            mail_groups={'failure':[],'outgoing':[]}
            forrecipientinmessage_info['notif']:
                partner,ntype,ngroup,nstatus=recipient['partner'],recipient['type'],recipient.get('group'),recipient.get('status','sent')
                nis_read,ncheck_send=recipient.get('is_read',Falseifrecipient['type']=='inbox'elseTrue),recipient.get('check_send',True)
                ifnotngroup:
                    ngroup='user'
                    ifpartnerandnotpartner.user_ids:
                        ngroup='customer'
                    elifpartnerandpartner.partner_share:
                        ngroup='portal'

                #findnotification
                partner_notif=notifications.filtered(
                    lambdan:n.mail_message_id==messageand
                    n.res_partner_id==partnerand
                    n.notification_type==ntypeand
                    n.notification_status==nstatusand
                    n.is_read==nis_read
                )
                self.assertTrue(partner_notif,'Mail:notfoundnotificationfor%s(type:%s,state:%s,message:%s)'%(partner,ntype,nstatus,message.id))

                #preparefurtherasserts
                ifntype=='email':
                    ifnstatus=='sent':
                        ifncheck_send:
                            email_groups[ngroup].append(partner)
                    #whenforce_sendisFalsenotably,notificationsarereadyandemailsoutgoing
                    elifnstatus=='ready':
                        mail_groups['outgoing'].append(partner)
                        ifncheck_send:
                            email_groups[ngroup].append(partner)
                    #canceled:currentlynothingchecked
                    elifnstatus=='exception':
                        mail_groups['failure'].append(partner)
                        ifncheck_send:
                            email_groups[ngroup].append(partner)
                    elifnstatus=='canceled':
                        pass
                    else:
                        raiseNotImplementedError()

                done_notifs|=partner_notif
            done_msgs|=message

            #checkbusnotificationsthatshouldbesent(hint:messageauthor,multiplenotifications)
            bus_notifications=message.notification_ids._filtered_for_web_client().filtered(lambdan:n.notification_status=='exception')
            ifbus_notifications:
                self.assertMessageBusNotifications(message)

            #checkemailsthatshouldbesent(hint:mail.mailpergroup,emailparrecipient)
            email_values={'body_content':mbody,
                            'references_content':message.message_id}
            ifmessage_info.get('email_values'):
                email_values.update(message_info['email_values'])
            forrecipientsinemail_groups.values():
                partners=self.env['res.partner'].sudo().concat(*recipients)
                ifall(pinmail_groups['failure']forpinpartners):
                    mail_status='exception'
                elifall(pinmail_groups['outgoing']forpinpartners):
                    mail_status='outgoing'
                else:
                    mail_status='sent'
                ifnotself.mail_unlink_sent:
                    self.assertMailMail(
                        partners,mail_status,
                        author=message_info.get('fields_values',{}).get('author_id')ormessage.author_idormessage.email_from,
                        mail_message=message,
                        email_values=email_values,
                        fields_values=message_info.get('fields_values'),
                    )
                else:
                    forrecipientinpartners:
                        self.assertSentEmail(
                            message.author_idifmessage.author_idelsemessage.email_from,
                            [recipient],
                            **email_values
                        )

            ifnotany(pforrecipientsinemail_groups.values()forpinrecipients):
                self.assertNoMail(partners,mail_message=message,author=message.author_id)

        returndone_msgs,done_notifs

    defassertMessageBusNotifications(self,message):
        """Assertsthattheexpectednotificationupdateshavebeensentonthe
        busforthegivenmessage."""
        self.assertBusNotifications(
            [(self.cr.dbname,'res.partner',message.author_id.id)],
            [{
                'type':'message_notification_update',
                'elements':message._message_notification_format(),
            }],
            check_unique=False
        )

    defassertBusNotifications(self,channels,message_items=None,check_unique=True):
        """Checkbusnotificationscontent.Mandatoryandbasiccheckisabout
        channelsbeingnotified.Contentcheckisoptional.

        EXPECTED
        :paramchannels:listofexpectedbuschannels,like[
          (self.cr.dbname,'mail.channel',self.channel_1.id),
          (self.cr.dbname,'res.partner',self.partner_employee_2.id)
        ]
        :parammessage_items:ifgiven,listofexpectedmessagemakingavalid
          pair(channel,message)tobefoundinbus.bus,like[
            {'type':'message_notification_update',
             'elements':{self.msg.id:{
                'message_id':self.msg.id,
                'message_type':'sms',
                'notifications':{...},
                ...
              }}
            },{...}]
        """
        bus_notifs=self.env['bus.bus'].sudo().search([('channel','in',[json_dump(channel)forchannelinchannels])])
        ifcheck_unique:
            self.assertEqual(len(bus_notifs),len(channels))
        self.assertEqual(set(bus_notifs.mapped('channel')),set([json_dump(channel)forchannelinchannels]))

        notif_messages=[n.messageforninbus_notifs]

        forexpectedinmessage_itemsor[]:
            fornotificationinnotif_messages:
                ifjson_dump(expected)==notification:
                    break
            else:
                raiseAssertionError('Nonotificationwasfoundwiththeexpectedvalue.\nExpected:\n%s\nReturned:\n%s'%
                    (json_dump(expected),'\n'.join([nforninnotif_messages])))

        returnbus_notifs

    defassertNotified(self,message,recipients_info,is_complete=False):
        """Lightweightcheckfornotifications(mail.notification).

        :paramrecipients_info:listnotifiedrecipients:[
          {'partner':res.partnerrecord(maybeempty),
           'type':notification_typetocheck,
           'is_read':is_readtocheck,
          },{...}]
        """
        notifications=self._new_notifs.filtered(lambdanotif:notifinmessage.notification_ids)
        ifis_complete:
            self.assertEqual(len(notifications),len(recipients_info))
        forrinfoinrecipients_info:
            recipient_notif=next(
                (notif
                 fornotifinnotifications
                 ifnotif.res_partner_id==rinfo['partner']
                ),False
            )
            self.assertTrue(recipient_notif)
            self.assertEqual(recipient_notif.is_read,rinfo['is_read'])
            self.assertEqual(recipient_notif.notification_type,rinfo['type'])

    defassertTracking(self,message,data):
        tracking_values=message.sudo().tracking_value_ids
        forfield_name,value_type,old_value,new_valueindata:
            tracking=tracking_values.filtered(lambdatrack:track.field.name==field_name)
            self.assertEqual(len(tracking),1)
            ifvalue_typein('char','integer'):
                self.assertEqual(tracking.old_value_char,old_value)
                self.assertEqual(tracking.new_value_char,new_value)
            elifvalue_typein('many2one'):
                self.assertEqual(tracking.old_value_integer,old_valueandold_value.idorFalse)
                self.assertEqual(tracking.new_value_integer,new_valueandnew_value.idorFalse)
                self.assertEqual(tracking.old_value_char,old_valueandold_value.display_nameor'')
                self.assertEqual(tracking.new_value_char,new_valueandnew_value.display_nameor'')
            else:
                self.assertEqual(1,0)


classMailCommon(common.SavepointCase,MailCase):
    """Almost-voidclassdefinitionsettingthesavepointcase+mockofmail.
    Usedmainlyforclassinheritanceinotherapplicationsandtestmodules."""

    @classmethod
    defsetUpClass(cls):
        super(MailCommon,cls).setUpClass()
        #givedefaultvaluesforallemailaliasesanddomain
        cls._init_mail_gateway()
        #ensureadminconfiguration
        cls.user_admin=cls.env.ref('base.user_admin')
        cls.user_admin.write({'notification_type':'inbox'})
        cls.partner_admin=cls.env.ref('base.partner_admin')
        cls.company_admin=cls.user_admin.company_id
        cls.company_admin.write({'email':'company@example.com'})

        #teststandardemployee
        cls.user_employee=mail_new_test_user(
            cls.env,login='employee',
            groups='base.group_user',
            company_id=cls.company_admin.id,
            name='ErnestEmployee',
            notification_type='inbox',
            signature='--\nErnest'
        )
        cls.partner_employee=cls.user_employee.partner_id
        cls.partner_employee.flush()

    @classmethod
    def_create_portal_user(cls):
        cls.user_portal=mail_new_test_user(
            cls.env,login='portal_test',groups='base.group_portal',company_id=cls.company_admin.id,
            name='ChellGladys',notification_type='email')
        cls.partner_portal=cls.user_portal.partner_id
        returncls.user_portal

    @classmethod
    def_activate_multi_company(cls):
        """Createanothercompany,addittoadminandcreateanuserthat
        belongstothatnewcompany.Itallowstotestflowswithusersfrom
        differentcompanies."""
        cls.company_2=cls.env['res.company'].create({
            'name':'Company2',
            'email':'company_2@test.example.com',
        })
        cls.user_admin.write({'company_ids':[(4,cls.company_2.id)]})

        cls.user_employee_c2=mail_new_test_user(
            cls.env,login='employee_c2',
            groups='base.group_user',
            company_id=cls.company_2.id,
            company_ids=[(4,cls.company_2.id)],
            name='EnguerrandEmployeeC2',
            notification_type='inbox',
            signature='--\nEnguerrand'
        )
        cls.partner_employee_c2=cls.user_employee_c2.partner_id
