#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mass_mailing.data.mail_test_dataimportMAIL_TEMPLATE
fromflectra.addons.test_mass_mailing.tests.commonimportTestMassMailCommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportusers
fromflectra.toolsimportemail_normalize,mute_logger


@tagged('mass_mailing')
classTestMassMailing(TestMassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassMailing,cls).setUpClass()

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_mailing_gateway_reply(self):
        customers=self.env['res.partner']
        forxinrange(0,3):
            customers|=self.env['res.partner'].create({
                'name':'Customer_%02d'%x,
                'email':'"Customer_%02d"<customer_%02d@test.example.com'%(x,x),
            })

        mailing=self.env['mailing.mailing'].create({
            'name':'TestName',
            'subject':'TestSubject',
            'body_html':'Hello${object.name}',
            'reply_to_mode':'email',
            'reply_to':'%s@%s'%(self.test_alias.alias_name,self.test_alias.alias_domain),
            'keep_archives':True,
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
            'mailing_domain':'%s'%[('id','in',customers.ids)],
        })
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing.action_send_mail()

        self.gateway_mail_reply_wrecord(MAIL_TEMPLATE,customers[0],use_in_reply_to=True)
        self.gateway_mail_reply_wrecord(MAIL_TEMPLATE,customers[1],use_in_reply_to=False)

        #customer2loosesheaders
        mail_mail=self._find_mail_mail_wrecord(customers[2])
        self.format_and_process(
            MAIL_TEMPLATE,
            mail_mail.email_to,
            mail_mail.reply_to,
            subject='Re:%s'%mail_mail.subject,
            extra='',
            msg_id='<123456.%s.%d@test.example.com>'%(customers[2]._name,customers[2].id),
            target_model=customers[2]._name,target_field=customers[2]._rec_name,
        )
        mailing.flush()

        #checktracesstatus
        traces=self.env['mailing.trace'].search([('model','=',customers._name),('res_id','in',customers.ids)])
        self.assertEqual(len(traces),3)
        customer0_trace=traces.filtered(lambdat:t.res_id==customers[0].id)
        self.assertEqual(customer0_trace.state,'replied')
        customer1_trace=traces.filtered(lambdat:t.res_id==customers[1].id)
        self.assertEqual(customer1_trace.state,'replied')
        customer2_trace=traces.filtered(lambdat:t.res_id==customers[2].id)
        self.assertEqual(customer2_trace.state,'sent')

        #checkmailingstatistics
        self.assertEqual(mailing.sent,3)
        self.assertEqual(mailing.delivered,3)
        self.assertEqual(mailing.opened,2)
        self.assertEqual(mailing.replied,2)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_gateway_update(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)
        recipients=self._create_mailing_test_records(model='mailing.test.optout',count=5)
        self.assertEqual(len(recipients),5)

        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mailing.test.optout'),
            'mailing_domain':[('id','in',recipients.ids)]
        })
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'email':record.email_normalized}
             forrecordinrecipients],
            mailing,recipients,
            mail_links_info=[[
                ('url0','https://www.flectra.tz/my/%s'%record.name,True,{}),
                ('url1','https://www.flectra.be',True,{}),
                ('url2','https://www.flectrahq.com',True,{}),
                ('url3','https://www.flectra.eu',True,{}),
                ('url4','https://www.example.com/foo/bar?baz=qux',True,{'baz':'qux'}),
                ('url5','%s/event/dummy-event-0'%mailing.get_base_url(),True,{}),
                #viewisnotshortenedandparsedatsending
                ('url6','%s/view'%mailing.get_base_url(),False,{}),
                ('url7','mailto:test@flectrahq.com',False,{}),
                #unsubscribeisnotshortenedandparsedatsending
                ('url8','%s/unsubscribe_from_list'%mailing.get_base_url(),False,{}),
            ]forrecordinrecipients],
            check_mail=True
        )
        self.assertMailingStatistics(mailing,expected=5,delivered=5,sent=5)

        #simulateaclick
        self.gateway_mail_click(mailing,recipients[0],'https://www.flectra.be')
        mailing.invalidate_cache()
        self.assertMailingStatistics(mailing,expected=5,delivered=5,sent=5,opened=1,clicked=1)

        #simulateabounce
        self.assertEqual(recipients[1].message_bounce,0)
        self.gateway_mail_bounce(mailing,recipients[1])
        mailing.invalidate_cache()
        self.assertMailingStatistics(mailing,expected=5,delivered=4,sent=5,opened=1,clicked=1,bounced=1)
        self.assertEqual(recipients[1].message_bounce,1)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_recipients(self):
        """Testrecipient-specificcomputation,withemail,formatting,
        multi-emails,...totestcornercases.Blacklistmixinimpactis
        tested."""
        (customer_mult,customer_fmt,customer_unic,
         customer_case,customer_weird,customer_weird_2
        )=self.env['res.partner'].create([
            {
                'email':'customer.multi.1@example.com,"TestMulti2"<customer.multi.2@example.com>',
                'name':'MultiEMail',
            },{
                'email':'"FormattedCustomer"<test.customer.format@example.com>',
                'name':'FormattedEmail',
            },{
                'email':'"UnicodeCustomer"<test.customer.😊@example.com>',
                'name':'UnicodeEmail',
            },{
                'email':'TEST.CUSTOMER.CASE@EXAMPLE.COM',
                'name':'CaseEmail',
            },{
                'email':'test.customer.weird@example.comWeirdFormat',
                'name':'WeirdFormatEmail',
            },{
                'email':'WeirdFormat2test.customer.weird.2@example.com',
                'name':'WeirdFormatEmail2',
            }
        ])

        #checkdifferenceofemailmanagementbetweenaclassicmodelandamodel
        #withan'email_normalized'field(blacklistmixin)
        fordst_modelin['mailing.test.customer','mailing.test.blacklist']:
            withself.subTest(dst_model=dst_model):
                (record_p_mult,record_p_fmt,record_p_unic,
                 record_p_case,record_p_weird,record_p_weird_2,
                 record_mult,record_fmt,record_unic
                )=self.env[dst_model].create([
                    {
                        'customer_id':customer_mult.id,
                    },{
                        'customer_id':customer_fmt.id,
                    },{
                        'customer_id':customer_unic.id,
                    },{
                        'customer_id':customer_case.id,
                    },{
                        'customer_id':customer_weird.id,
                    },{
                        'customer_id':customer_weird_2.id,
                    },{
                        'email_from':'record.multi.1@example.com,"RecordMulti2"<record.multi.2@example.com>',
                    },{
                        'email_from':'"FormattedRecord"<record.format@example.com>',
                    },{
                        'email_from':'"UnicodeRecord"<record.😊@example.com>',
                    }
                ])
                test_records=(
                    record_p_mult+record_p_fmt+record_p_unic+
                    record_p_case+record_p_weird+record_p_weird_2+
                    record_mult+record_fmt+record_unic
                )
                mailing=self.env['mailing.mailing'].create({
                    'body_html':"""<div><p>Hello${object.name}</p>""",
                    'mailing_domain':[('id','in',test_records.ids)],
                    'mailing_model_id':self.env['ir.model']._get_id(dst_model),
                    'mailing_type':'mail',
                    'name':'SourceName',
                    'preview':'Hi${object.name}:)',
                    'reply_to_mode':'thread',
                    'subject':'MailingSubject',
                })

                withself.mock_mail_gateway(mail_unlink_sent=False):
                    mailing.action_send_mail()

                #Differenceinemail,email_to_recipientsandemail_to_mail
                #->email:traceemail:normalized,toeaseitsmanagement,mainlytechnical
                #->email_to_mail:mail.mailemail:email_tostoredinoutgoingmail.mail(canbemulti)
                #->email_to_recipients:email_toforoutgoingemails,listmeansseveralrecipients
                self.assertMailTraces(
                    [
                        {'email':'customer.multi.1@example.com',
                         'email_to_recipients':[[f'"{customer_mult.name}"<customer.multi.1@example.com>',f'"{customer_mult.name}"<customer.multi.2@example.com>']],
                         'failure_type':False,
                         'partner':customer_mult,
                         'state':'sent'},
                        {'email':'test.customer.format@example.com',
                         #mailtoavoidsdoubleencapsulation
                         'email_to_recipients':[[f'"{customer_fmt.name}"<test.customer.format@example.com>']],
                         'failure_type':False,
                         'partner':customer_fmt,
                         'state':'sent'},
                        {'email':'test.customer.😊@example.com',
                         #mailtoavoidsdoubleencapsulation
                         'email_to_recipients':[[f'"{customer_unic.name}"<test.customer.😊@example.com>']],
                         'failure_type':False,
                         'partner':customer_unic,
                         'state':'sent'},
                        {'email':'test.customer.case@example.com',
                         'email_to_recipients':[[f'"{customer_case.name}"<test.customer.case@example.com>']],
                         'failure_type':False,
                         'partner':customer_case,
                         'state':'sent'}, #lowercased
                        {'email':'test.customer.weird@example.comweirdformat',
                         'email_to_recipients':[[f'"{customer_weird.name}"<test.customer.weird@example.comweirdformat>']],
                         'failure_type':False,
                         'partner':customer_weird,
                         'state':'sent'}, #concatenateseverythingafterdomain
                        {'email':'test.customer.weird.2@example.com',
                        'email_to_recipients':[[f'"{customer_weird_2.name}"<test.customer.weird.2@example.com>']],
                         'failure_type':False,
                         'partner':customer_weird_2,
                         'state':'sent'},
                        {'email':'record.multi.1@example.com',
                         'email_to_mail':'record.multi.1@example.com,record.multi.2@example.com',
                         'email_to_recipients':[['record.multi.1@example.com','record.multi.2@example.com']],
                         'failure_type':False,
                         'state':'sent'},
                        {'email':'record.format@example.com',
                         'failure_type':False,
                         'state':'sent'},
                        {'email':'record.😊@example.com',
                         'failure_type':False,
                         'state':'sent'},
                    ],
                    mailing,
                    test_records,
                    check_mail=True,
                )

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_reply_to_mode_new(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)
        recipients=self._create_mailing_test_records(model='mailing.test.blacklist',count=5)
        self.assertEqual(len(recipients),5)
        initial_messages=recipients.message_ids
        mailing.write({
            'mailing_domain':[('id','in',recipients.ids)],
            'keep_archives':False,
            'reply_to_mode':'email',
            'reply_to':self.test_alias.display_name,
        })

        withself.mock_mail_gateway(mail_unlink_sent=True):
            mailing.action_send_mail()

        answer_rec=self.gateway_mail_reply_wemail(MAIL_TEMPLATE,recipients[0].email_normalized,target_model=self.test_alias.alias_model_id.model)
        self.assertTrue(bool(answer_rec))
        self.assertEqual(answer_rec.name,'Re:%s'%mailing.subject)
        self.assertEqual(
            answer_rec.message_ids.subject,'Re:%s'%mailing.subject,
            'Answershouldbelogged')
        self.assertEqual(recipients.message_ids,initial_messages)

        self.assertMailingStatistics(mailing,expected=5,delivered=5,sent=5,opened=1,replied=1)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_reply_to_mode_update(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)
        recipients=self._create_mailing_test_records(model='mailing.test.blacklist',count=5)
        self.assertEqual(len(recipients),5)
        mailing.write({
            'mailing_domain':[('id','in',recipients.ids)],
            'keep_archives':False,
            'reply_to_mode':'thread',
            'reply_to':self.test_alias.display_name,
        })

        withself.mock_mail_gateway(mail_unlink_sent=True):
            mailing.action_send_mail()

        answer_rec=self.gateway_mail_reply_wemail(MAIL_TEMPLATE,recipients[0].email_normalized,target_model=self.test_alias.alias_model_id.model)
        self.assertFalse(bool(answer_rec))
        self.assertEqual(
            recipients[0].message_ids[1].subject,mailing.subject,
            'Shouldhavekeepalog(toenablethread-basedanswer)')
        self.assertEqual(
            recipients[0].message_ids[0].subject,'Re:%s'%mailing.subject,
            'Answershouldbelogged')

        self.assertMailingStatistics(mailing,expected=5,delivered=5,sent=5,opened=1,replied=1)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_mailing_trace_utm(self):
        """TestmailingUTMsarecaughtonreply"""
        self._create_mailing_list()
        self.test_alias.write({
            'alias_model_id':self.env['ir.model']._get('mailing.test.utm').id
        })

        source=self.env['utm.source'].create({'name':'Sourcetest'})
        medium=self.env['utm.medium'].create({'name':'Mediumtest'})
        campaign=self.env['utm.campaign'].create({'name':'Campaigntest'})
        subject='MassMailingTestUTM'

        mailing=self.env['mailing.mailing'].create({
            'name':'UTMTest',
            'subject':subject,
            'body_html':'<p>Hello${object.name}</p>',
            'reply_to_mode':'email',
            'reply_to':'%s@%s'%(self.test_alias.alias_name,self.test_alias.alias_domain),
            'keep_archives':True,
            'mailing_model_id':self.env['ir.model']._get('mailing.list').id,
            'contact_list_ids':[(4,self.mailing_list_1.id)],
            'source_id':source.id,
            'medium_id':medium.id,
            'campaign_id':campaign.id
        })

        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        traces=self.env['mailing.trace'].search([('model','=',self.mailing_list_1.contact_ids._name),('res_id','in',self.mailing_list_1.contact_ids.ids)])
        self.assertEqual(len(traces),3)

        #simulateresponsetomailing
        self.gateway_mail_reply_wrecord(MAIL_TEMPLATE,self.mailing_list_1.contact_ids[0],use_in_reply_to=True)
        self.gateway_mail_reply_wrecord(MAIL_TEMPLATE,self.mailing_list_1.contact_ids[1],use_in_reply_to=False)

        mailing_test_utms=self.env['mailing.test.utm'].search([('name','=','Re:%s'%subject)])
        self.assertEqual(len(mailing_test_utms),2)
        fortest_utminmailing_test_utms:
            self.assertEqual(test_utm.campaign_id,campaign)
            self.assertEqual(test_utm.source_id,source)
            self.assertEqual(test_utm.medium_id,medium)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_w_blacklist(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)
        recipients=self._create_mailing_test_records(count=5)

        #blacklistrecords2,3,4
        self.env['mail.blacklist'].create({'email':recipients[2].email_normalized})
        self.env['mail.blacklist'].create({'email':recipients[3].email_normalized})
        self.env['mail.blacklist'].create({'email':recipients[4].email_normalized})

        #unblacklistrecord2
        self.env['mail.blacklist'].action_remove_with_reason(
            recipients[2].email_normalized,"humanerror"
        )
        self.env['mail.blacklist'].flush(['active'])

        mailing.write({'mailing_domain':[('id','in',recipients.ids)]})
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'email':'test.record.00@test.example.com'},
             {'email':'test.record.01@test.example.com'},
             {'email':'test.record.02@test.example.com'},
             {'email':'test.record.03@test.example.com','state':'ignored','failure_type':False},
             {'email':'test.record.04@test.example.com','state':'ignored','failure_type':False}],
            mailing,recipients,check_mail=True
        )
        self.assertEqual(mailing.ignored,2)

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_w_opt_out(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)
        recipients=self._create_mailing_test_records(model='mailing.test.optout',count=5)

        #optoutrecords0and1
        (recipients[0]|recipients[1]).write({'opt_out':True})
        #blacklistrecords4
        self.env['mail.blacklist'].create({'email':recipients[4].email_normalized})

        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mailing.test.optout'),
            'mailing_domain':[('id','in',recipients.ids)]
        })
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'email':'test.record.00@test.example.com','state':'ignored','failure_type':False},
             {'email':'test.record.01@test.example.com','state':'ignored','failure_type':False},
             {'email':'test.record.02@test.example.com'},
             {'email':'test.record.03@test.example.com'},
             {'email':'test.record.04@test.example.com','state':'ignored','failure_type':False}],
            mailing,recipients,check_mail=True
        )
        self.assertEqual(mailing.ignored,3)

    @users('user_marketing')
    deftest_mailing_w_seenlist(self):
        """
        Testswhetherfunction`_get_seen_list`iscorrectlyabletoidentifyduplicateemails,
        eventhroughdifferentbatches.
        Mailsusedifferentnamestomakesuretheyarerecognizedasduplicatesevenwithoutbeing
        normalized(e.g.:'"jc"<0@example.com>'and'"vd"<0@example.com>'areduplicates)
        """
        BATCH_SIZE=5
        names=['jc','vd']
        emails=[f'test.{i}@example.com'foriinrange(BATCH_SIZE)]
        records=self.env['mailing.test.partner'].create([{
            'name':f'test_duplicates{i}','email_from':f'"{names[i%2]}"<{emails[i%BATCH_SIZE]}>'
        }foriinrange(20)])

        mailing=self.env['mailing.mailing'].create({
            'mailing_domain':[('name','ilike','test_duplicates%')],
            'mailing_model_id':self.env.ref('test_mass_mailing.model_mailing_test_partner').id,
            'name':'testduplicates',
            'subject':'testduplicates',
        })

        withself.mock_mail_gateway():
            foriinrange(0,20,BATCH_SIZE):
                mailing.action_send_mail(records[i:i+BATCH_SIZE].mapped('id'))
            self.assertEqual(len(self._mails),BATCH_SIZE)
            self.assertEqual(mailing.ignored,15)
            mails_sent=[email_normalize(mail['email_to'][0])formailinself._mails]
            foremailinemails:
                self.assertEqual(mails_sent.count(email),1)

    @users('user_marketing')
    deftest_mailing_w_seenlist_unstored_partner(self):
        """Testseenlistwhenpartnersarenotstored."""
        test_customers=self.env['res.partner'].sudo().create([
            {'email':f'"MailingPartner{idx}"<email.from.{idx}@test.example.com',
             'name':f'MailingPartner{idx}',
            }foridxinrange(8)
        ])
        test_records=self.env['mailing.test.partner.unstored'].create([
            {'email_from':f'email.from.{idx}@test.example.com',
             'name':f'MailingRecord{idx}',
            }foridxinrange(10)
        ])
        self.assertEqual(test_records[:8].partner_id,test_customers)
        self.assertFalse(test_records[9:].partner_id)

        mailing=self.env['mailing.mailing'].create({
            'body_html':'<p>Marketingstufffor${object.name}</p>',
            'mailing_domain':[('id','in',test_records.ids)],
            'mailing_model_id':self.env['ir.model']._get_id('mailing.test.partner.unstored'),
            'name':'test',
            'subject':'Blacklisted',
        })

        #createexistingtracestochecktheseenlist
        traces=self._create_sent_traces(
            mailing,
            test_records[:3]
        )
        traces.flush()

        #checkremainingrecipientseffectivelycheckseenlist
        mailing.action_put_in_queue()
        res_ids=mailing._get_remaining_recipients()
        self.assertEqual(sorted(res_ids),sorted(test_records[3:].ids))

        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing.action_send_mail(res_ids=test_records.ids)
        self.assertEqual(len(self._mails),7,'Mailing:seenlistshouldcontain3existingtraces')

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_mailing_list_optout(self):
        """Testmailinglistmodelspecificoptoutbehavior"""
        mailing_contact_1=self.env['mailing.contact'].create({'name':'test1A','email':'test@test.example.com'})
        mailing_contact_2=self.env['mailing.contact'].create({'name':'test1B','email':'test@test.example.com'})
        mailing_contact_3=self.env['mailing.contact'].create({'name':'test3','email':'test3@test.example.com'})
        mailing_contact_4=self.env['mailing.contact'].create({'name':'test4','email':'test4@test.example.com'})
        mailing_contact_5=self.env['mailing.contact'].create({'name':'test5','email':'test5@test.example.com'})

        #createmailinglistrecord
        mailing_list_1=self.env['mailing.list'].create({
            'name':'A',
            'contact_ids':[
                (4,mailing_contact_1.id),
                (4,mailing_contact_2.id),
                (4,mailing_contact_3.id),
                (4,mailing_contact_5.id),
            ]
        })
        mailing_list_2=self.env['mailing.list'].create({
            'name':'B',
            'contact_ids':[
                (4,mailing_contact_3.id),
                (4,mailing_contact_4.id),
            ]
        })
        #contact_1isoptoutbutsameemailisnotoptoutfromthesamelist
        #contact3isoptoutinlist1butnotinlist2
        #contact5isoptout
        Sub=self.env['mailing.contact.subscription']
        Sub.search([('contact_id','=',mailing_contact_1.id),('list_id','=',mailing_list_1.id)]).write({'opt_out':True})
        Sub.search([('contact_id','=',mailing_contact_3.id),('list_id','=',mailing_list_1.id)]).write({'opt_out':True})
        Sub.search([('contact_id','=',mailing_contact_5.id),('list_id','=',mailing_list_1.id)]).write({'opt_out':True})

        #createmassmailingrecord
        mailing=self.env['mailing.mailing'].create({
            'name':'SourceName',
            'subject':'MailingSubject',
            'body_html':'<p>Hello${object.name}</p>',
            'mailing_model_id':self.env['ir.model']._get('mailing.list').id,
            'contact_list_ids':[(4,ml.id)formlinmailing_list_1|mailing_list_2],
        })
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing._process_mass_mailing_queue()

        self.assertMailTraces(
            [{'email':'test@test.example.com','state':'sent'},
             {'email':'test@test.example.com','state':'ignored','failure_type':False},
             {'email':'test3@test.example.com'},
             {'email':'test4@test.example.com'},
             {'email':'test5@test.example.com','state':'ignored','failure_type':False}],
            mailing,
            mailing_contact_1+mailing_contact_2+mailing_contact_3+mailing_contact_4+mailing_contact_5,
            check_mail=True
        )
        self.assertEqual(mailing.ignored,2)
