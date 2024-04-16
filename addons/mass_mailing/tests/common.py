#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
importrandom
importre
importwerkzeug

fromflectra.addons.link_tracker.tests.commonimportMockLinkTracker
fromflectra.addons.mail.tests.commonimportMailCase,MailCommon,mail_new_test_user
fromflectraimporttools

classMassMailCase(MailCase,MockLinkTracker):

    #------------------------------------------------------------
    #ASSERTS
    #------------------------------------------------------------

    defassertMailingStatistics(self,mailing,**kwargs):
        """Helpertoassertmailingstatisticsfields.Aswehavemanyofthem
        ithelpslesseningtestasserts."""
        ifnotkwargs.get('expected'):
            kwargs['expected']=len(mailing.mailing_trace_ids)
        ifnotkwargs.get('delivered'):
            kwargs['delivered']=len(mailing.mailing_trace_ids)
        forfnamein['scheduled','expected','sent','delivered',
                      'opened','replied','clicked',
                      'ignored','failed','bounced']:
            self.assertEqual(
                mailing[fname],kwargs.get(fname,0),
                'Mailing%sstatisticsfailed:got%sinsteadof%s'%(fname,mailing[fname],kwargs.get(fname,0))
            )

    defassertMailTraces(self,recipients_info,mailing,records,
                         check_mail=True,sent_unlink=False,
                         author=None,mail_links_info=None):
        """Checkcontentoftraces.Tracesarefetchedbasedonagivenmailing
        andrecords.Theircontentiscomparedtorecipients_infostructurethat
        holdsexpectedinformation.Linkscontentmaybechecked,notablyto
        assertshorteningorunsubscribelinks.Mail.mailrecordsmayoptionally
        bechecked.

        :paramrecipients_info:list[{
            #TRACE
            'partner':res.partnerrecord(maybeempty),
            'email':emailusedwhensendingemail(maybeempty,computedbasedonpartner),
            'state':outgoing/sent/ignored/bounced/exception/opened(sentbydefault),
            'record:linkedrecord,
            #MAIL.MAIL
            'content':optionalcontentthatshouldbepresentinmail.mailbody_html;
            'email_to_mail':optionalemailusedforthemail,whendifferentfromthe
              onestoredonthetraceitself;
            'email_to_recipients':optional,see'_assertMailMail';
            'failure_type':optionalfailurereason;
            },{...}]

        :parammailing:amailing.mailingrecordfromwhichtraceshavebeen
          generated;
        :paramrecords:recordsgiventomailingthatgeneratedtraces.Itis
          usednotablytofindtracesusingtheirIDs;
        :paramcheck_mail:ifTrue,alsocheckmail.mailrecordsthatshouldbe
          linkedtotraces;
        :paramsent_unlink:itTrue,sentmail.mailaredeletedandwecheckgateway
          outputresultinsteadofactualmail.mailrecords;
        :parammail_links_info:ifgiven,shouldfolloworderof``recipients_info``
          andgivedetailsaboutlinks.See``assertLinkShortenedHtml``helperfor
          moredetailsaboutcontenttogive;
        :paramauthor:authorofsentmail.mail;
        """
        #maptracestatetoemailstate
        state_mapping={
            'sent':'sent',
            'opened':'sent', #openedimpliessomethinghasbeensent
            'replied':'sent', #repliedimpliessomethinghasbeensent
            'ignored':'cancel',
            'exception':'exception',
            'canceled':'cancel',
            'bounced':'cancel',
        }

        traces=self.env['mailing.trace'].search([
            ('mass_mailing_id','in',mailing.ids),
            ('res_id','in',records.ids)
        ])
        debug_info='\n'.join(
            (
                f'Trace:to{t.email}-state{t.state}-res_id{t.res_id}'
                fortintraces
            )
        )

        #ensuretracecoherency
        self.assertTrue(all(s.model==records._nameforsintraces))
        self.assertEqual(set(s.res_idforsintraces),set(records.ids))

        #checkeachtraces
        ifnotmail_links_info:
            mail_links_info=[None]*len(recipients_info)
        forrecipient_info,link_info,recordinzip(recipients_info,mail_links_info,records):
            partner=recipient_info.get('partner',self.env['res.partner'])
            email=recipient_info.get('email')
            email_to_mail=recipient_info.get('email_to_mail')oremail
            email_to_recipients=recipient_info.get('email_to_recipients')
            state=recipient_info.get('state','sent')
            record=recordorrecipient_info.get('record')
            content=recipient_info.get('content')
            ifemailisNoneandpartner:
                email=partner.email_normalized

            recipient_trace=traces.filtered(
                lambdat:(t.email==emailor(notemailandnott.email))and\
                          t.state==stateand\
                          (t.res_id==record.idifrecordelseTrue)
            )
            self.assertTrue(
                len(recipient_trace)==1,
                'MailTrace:email%s(recipient%s,state:%s,record:%s):found%srecords(1expected)\n%s'%(
                    email,partner,state,record,
                    len(recipient_trace),debug_info)
            )
            self.assertTrue(bool(recipient_trace.mail_mail_id_int))
            if'failure_type'inrecipient_infoorstatein('ignored','exception','canceled','bounced'):
                self.assertEqual(recipient_trace.failure_type,recipient_info['failure_type'])

            ifcheck_mail:
                ifauthorisNone:
                    author=self.env.user.partner_id

                fields_values={'mailing_id':mailing}
                ifrecipient_info.get('mail_values'):
                    fields_values.update(recipient_info['mail_values'])
                if'failure_reason'inrecipient_info:
                    fields_values['failure_reason']=recipient_info['failure_reason']

                #specificforpartner:email_formattedisused
                ifpartner:
                    ifstate=='sent'andsent_unlink:
                        self.assertSentEmail(author,[partner])
                    else:
                        self.assertMailMail(
                            partner,state_mapping[state],
                            author=author,
                            content=content,
                            email_to_recipients=email_to_recipients,
                            fields_values=fields_values,
                        )
                #specificifemailisFalse->couldhavetroublesfindingitifseveralfalsytraces
                elifnotemailandstatein('ignored','canceled','bounced'):
                    self.assertMailMailWId(
                        recipient_trace.mail_mail_id_int,state_mapping[state],
                        author=author,
                        content=content,
                        email_to_recipients=email_to_recipients,
                        fields_values=fields_values,
                    )
                else:
                    self.assertMailMailWEmails(
                        [email_to_mail],state_mapping[state],
                        author=author,
                        content=content,
                        email_to_recipients=email_to_recipients,
                        fields_values=fields_values,
                    )

            iflink_info:
                trace_mail=self._find_mail_mail_wrecord(record)
                for(anchor_id,url,is_shortened,add_link_params)inlink_info:
                    link_params={'utm_medium':'Email','utm_source':mailing.name}
                    ifadd_link_params:
                        link_params.update(**add_link_params)
                    self.assertLinkShortenedHtml(
                        trace_mail.body_html,
                        (anchor_id,url,is_shortened),
                        link_params=link_params,
                    )

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    defgateway_mail_bounce(self,mailing,record,bounce_base_values=None):
        """Generateabounceatmailgatewaylevel.

        :parammailing:a``mailing.mailing``recordonwhichwefindatrace
          tobounce;
        :paramrecord:recordwhichshouldbounce;
        :parambounce_base_values:optionalvaluesgiventorouting;
        """
        trace=mailing.mailing_trace_ids.filtered(
            lambdat:t.model==record._nameandt.res_id==record.id
        )

        parsed_bounce_values={
            'email_from':'some.email@external.example.com', #TDEcheck:email_from->traceemail?
            'to':'bounce@test.example.com', #TDEcheck:bouncealias?
            'message_id':tools.generate_tracking_message_id('MailTest'),
            'bounced_partner':self.env['res.partner'].sudo(),
            'bounced_message':self.env['mail.message'].sudo()
        }
        ifbounce_base_values:
            parsed_bounce_values.update(bounce_base_values)
        parsed_bounce_values.update({
            'bounced_email':trace.email,
            'bounced_msg_id':[trace.message_id],
        })
        self.env['mail.thread']._routing_handle_bounce(False,parsed_bounce_values)
        returntrace

    defgateway_mail_click(self,mailing,record,click_label):
        """Simulateaclickonasentemail.

        :parammailing:a``mailing.mailing``recordonwhichwefindatrace
          toclick;
        :paramrecord:recordwhichshouldclick;
        :paramclick_label:labeloflinkonwhichweshouldclick;
        """
        trace=mailing.mailing_trace_ids.filtered(
            lambdat:t.model==record._nameandt.res_id==record.id
        )

        email=self._find_sent_mail_wemail(trace.email)
        self.assertTrue(bool(email))
        for(_url_href,link_url,_dummy,label)inre.findall(tools.HTML_TAG_URL_REGEX,email['body']):
            iflabel==click_labeland'/r/'inlink_url: #shortenedlink,like'http://localhost:7073/r/LBG/m/53'
                parsed_url=werkzeug.urls.url_parse(link_url)
                path_items=parsed_url.path.split('/')
                code,trace_id=path_items[2],int(path_items[4])
                self.assertEqual(trace.id,trace_id)

                self.env['link.tracker.click'].sudo().add_click(
                    code,
                    ip='100.200.300.%3f'%random.random(),
                    country_code='BE',
                    mailing_trace_id=trace.id
                )
                break
        else:
            raiseAssertionError('url%snotfoundinmailing%sforrecord%s'%(click_label,mailing,record))
        returntrace

    defgateway_mail_open(self,mailing,record):
        """Simulateopeninganemailthroughblank.gificonaccess.Aswe
        don'twanttousethewholeHttplayerjustforthatwewilljust
        call'set_opened()'ontrace,untilhavingabetteroption.

        :parammailing:a``mailing.mailing``recordonwhichwefindatrace
          toopen;
        :paramrecord:recordwhichshouldopen;
        """
        trace=mailing.mailing_trace_ids.filtered(
            lambdat:t.model==record._nameandt.res_id==record.id
        )
        mail_mail_id_int=trace.mail_mail_id_int
        self.assertTrue(bool(mail_mail_id_int))
        trace.set_opened(mail_mail_ids=[mail_mail_id_int])
        returntrace

    @classmethod
    def_create_bounce_trace(cls,mailing,records,dt=None):
        ifdtisNone:
            dt=datetime.datetime.now()-datetime.timedelta(days=1)
        returncls._create_traces(mailing,records,bounced=dt)

    @classmethod
    def_create_sent_traces(cls,mailing,records,dt=None):
        ifdtisNone:
            dt=datetime.datetime.now()-datetime.timedelta(days=1)
        returncls._create_traces(mailing,records,sent=dt)

    @classmethod
    def_create_traces(cls,mailing,records,**values):
        if'email_normalized'inrecords:
            fname='email_normalized'
        elif'email_from'inrecords:
            fname='email_from'
        else:
            fname='email'
        randomized=random.random()
        traces=cls.env['mailing.trace'].create([
            dict({'mass_mailing_id':mailing.id,
                  'model':record._name,
                  'res_id':record.id,
                  #TDEFIXME:improvethiswithamail-enabledheuristics
                  'email':record[fname],
                  'message_id':'<%5f@gilbert.boitempomils>'%randomized,
                 },**values)
            forrecordinrecords
        ])
        returntraces

    @classmethod
    def_create_mailing_list(cls):
        """Shortcuttocreatemailinglists.Currentlyhardcoded,maybeevolve
        inanearfuture."""
        cls.mailing_list_1=cls.env['mailing.list'].with_context(cls._test_context).create({
            'name':'List1',
            'contact_ids':[
                (0,0,{'name':'Déboulonneur','email':'fleurus@example.com'}),
                (0,0,{'name':'Gorramts','email':'gorramts@example.com'}),
                (0,0,{'name':'Ybrant','email':'ybrant@example.com'}),
            ]
        })
        cls.mailing_list_2=cls.env['mailing.list'].with_context(cls._test_context).create({
            'name':'List2',
            'contact_ids':[
                (0,0,{'name':'Gilberte','email':'gilberte@example.com'}),
                (0,0,{'name':'GilberteEnMieux','email':'gilberte@example.com'}),
                (0,0,{'name':'Norbert','email':'norbert@example.com'}),
                (0,0,{'name':'Ybrant','email':'ybrant@example.com'}),
            ]
        })


classMassMailCommon(MailCommon,MassMailCase):

    @classmethod
    defsetUpClass(cls):
        super(MassMailCommon,cls).setUpClass()

        cls.user_marketing=mail_new_test_user(
            cls.env,login='user_marketing',
            groups='base.group_user,base.group_partner_manager,mass_mailing.group_mass_mailing_user',
            name='MartialMarketing',signature='--\nMartial')

        cls.email_reply_to='MyCompanySomehowAlias<test.alias@test.mycompany.com>'

        cls.env['base'].flush()
