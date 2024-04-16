#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

fromflectra.addons.test_mail_full.tests.commonimportTestMailFullCommon
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger
fromflectra.testsimporttagged


@tagged('mass_mailing')
classTestMassMailing(TestMailFullCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassMailing,cls).setUpClass()

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mailing_w_blacklist_opt_out(self):
        mailing=self.env['mailing.mailing'].browse(self.mailing_bl.ids)

        mailing.write({'mailing_model_id':self.env['ir.model']._get('mailing.test.optout').id})
        recipients=self._create_mailing_test_records(model='mailing.test.optout',count=10)

        #optoutrecords1and2
        (recipients[1]|recipients[2]).write({'opt_out':True})
        #blacklistrecords3and4
        self.env['mail.blacklist'].create({'email':recipients[3].email_normalized})
        self.env['mail.blacklist'].create({'email':recipients[4].email_normalized})
        #haveaduplicateemailfor9
        recipient_dup_1=recipients[9].copy()
        #haveavoidmail
        recipient_void_1=self.env['mailing.test.optout'].create({'name':'TestRecord_void_1'})
        #haveafalsymail
        recipient_falsy_1=self.env['mailing.test.optout'].create({
            'name':'TestRecord_falsy_1',
            'email_from':'falsymail'
        })
        recipients_all=recipients+recipient_dup_1+recipient_void_1+recipient_falsy_1

        mailing.write({'mailing_domain':[('id','in',recipients_all.ids)]})
        mailing.action_put_in_queue()
        withself.mock_mail_gateway(mail_unlink_sent=False):
            mailing.action_send_mail()

        forrecipientinrecipients_all:
            recipient_info={
                'email':recipient.email_normalized,
                'content':'Hello%s'%recipient.name}
            #opt-out:ignored(cancelmail)
            ifrecipientinrecipients[1]|recipients[2]:
                recipient_info['failure_type']=False
                recipient_info['state']='ignored'
            #blacklisted:ignored(cancelmail)
            elifrecipientinrecipients[3]|recipients[4]:
                recipient_info['failure_type']=False
                recipient_info['state']='ignored'
            #duplicates:ignored(cancelmail)
            elifrecipient==recipient_dup_1:
                recipient_info['failure_type']=False
                recipient_info['state']='ignored'
            #void:ignored(cancelmail)
            elifrecipient==recipient_void_1:
                recipient_info['failure_type']=False
                recipient_info['state']='ignored'
            #falsy:ignored(cancelmail)
            elifrecipient==recipient_falsy_1:
                recipient_info['failure_type']=False
                recipient_info['state']='ignored'
                recipient_info['email']=recipient.email_from #normalizedisFalsebutemailshouldbefalsymail
            else:
                email=self._find_sent_mail_wemail(recipient.email_normalized)
                #previewcorrectlyintegratedrenderedjinja
                self.assertIn(
                    'Hi%s:)'%recipient.name,
                    email['body'])
                #renderedunsubscribe
                self.assertIn(
                    '%s/mail/mailing/%s/unsubscribe'%(mailing.get_base_url(),mailing.id),
                    email['body'])
                unsubscribe_href=self._get_href_from_anchor_id(email['body'],"url6")
                unsubscribe_url=werkzeug.urls.url_parse(unsubscribe_href)
                unsubscribe_params=unsubscribe_url.decode_query().to_dict(flat=True)
                self.assertEqual(int(unsubscribe_params['res_id']),recipient.id)
                self.assertEqual(unsubscribe_params['email'],recipient.email_normalized)
                self.assertEqual(
                    mailing._unsubscribe_token(unsubscribe_params['res_id'],(unsubscribe_params['email'])),
                    unsubscribe_params['token']
                )
                #renderedview
                self.assertIn(
                    '%s/mailing/%s/view'%(mailing.get_base_url(),mailing.id),
                    email['body'])
                view_href=self._get_href_from_anchor_id(email['body'],"url6")
                view_url=werkzeug.urls.url_parse(view_href)
                view_params=view_url.decode_query().to_dict(flat=True)
                self.assertEqual(int(view_params['res_id']),recipient.id)
                self.assertEqual(view_params['email'],recipient.email_normalized)
                self.assertEqual(
                    mailing._unsubscribe_token(view_params['res_id'],(view_params['email'])),
                    view_params['token']
                )

            self.assertMailTraces(
                [recipient_info],mailing,recipient,
                mail_links_info=[[
                    ('url0','https://www.flectra.tz/my/%s'%recipient.name,True,{}),
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
                ]],
                check_mail=True,)

        #sent:13,2bl,2opt-out,3invalid->6remaining
        self.assertMailingStatistics(mailing,expected=13,delivered=6,sent=6,ignored=7)
