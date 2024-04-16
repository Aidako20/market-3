#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectra.addons.base.tests.commonimportTransactionCaseWithUserDemo
fromflectra.tests.commonimportusers,warmup
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger,formataddr


@tagged('mail_performance','post_install','-at_install')
classBaseMailPerformance(TransactionCaseWithUserDemo):

    defsetUp(self):
        super(BaseMailPerformance,self).setUp()
        self._quick_create_ctx={
            'no_reset_password':True,
            'mail_create_nolog':True,
            'mail_create_nosubscribe':True,
            'mail_notrack':True,
        }
        self.user_employee=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'ErnestEmployee',
            'login':'emp',
            'email':'e.e@example.com',
            'signature':'--\nErnest',
            'notification_type':'inbox',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id,self.env.ref('base.group_partner_manager').id])],
        })

        #patchregistrytosimulateareadyenvironment
        self.patch(self.env.registry,'ready',True)

    def_init_mail_gateway(self):
        #setupmailgateway
        self.alias_domain='example.com'
        self.alias_catchall='catchall.test'
        self.alias_bounce='bounce.test'
        self.default_from='notifications'
        self.env['ir.config_parameter'].set_param('mail.bounce.alias',self.alias_bounce)
        self.env['ir.config_parameter'].set_param('mail.catchall.domain',self.alias_domain)
        self.env['ir.config_parameter'].set_param('mail.catchall.alias',self.alias_catchall)
        self.env['ir.config_parameter'].set_param('mail.default.from',self.default_from)


@tagged('mail_performance','post_install','-at_install')
classTestBaseMailPerformance(BaseMailPerformance):

    defsetUp(self):
        super(TestBaseMailPerformance,self).setUp()

        self.res_partner_3=self.env['res.partner'].create({
            'name':'GeminiFurniture',
            'email':'gemini.furniture39@example.com',
        })
        self.res_partner_4=self.env['res.partner'].create({
            'name':'ReadyMat',
            'email':'ready.mat28@example.com',
        })
        self.res_partner_10=self.env['res.partner'].create({
            'name':'TheJacksonGroup',
            'email':'jackson.group82@example.com',
        })
        self.res_partner_12=self.env['res.partner'].create({
            'name':'AzureInterior',
            'email':'azure.Interior24@example.com',
        })
        self.env['mail.performance.thread'].create([
            {
                'name':'Object0',
                'value':0,
                'partner_id':self.res_partner_3.id,
            },{
                'name':'Object1',
                'value':10,
                'partner_id':self.res_partner_3.id,
            },{
                'name':'Object2',
                'value':20,
                'partner_id':self.res_partner_4.id,
            },{
                'name':'Object3',
                'value':30,
                'partner_id':self.res_partner_10.id,
            },{
                'name':'Object4',
                'value':40,
                'partner_id':self.res_partner_12.id,
            }
        ])

        self._init_mail_gateway()

    @users('__system__','demo')
    @warmup
    deftest_read_mail(self):
        """Readrecordsinheritingfrom'mail.thread'."""
        records=self.env['mail.performance.thread'].search([])
        self.assertEqual(len(records),5)

        withself.assertQueryCount(__system__=2,demo=2):
            #withoutcache
            forrecordinrecords:
                record.partner_id.country_id.name

        withself.assertQueryCount(0):
            #withcache
            forrecordinrecords:
                record.partner_id.country_id.name

        withself.assertQueryCount(0):
            #value_pcmusthavebeenprefetched,too
            forrecordinrecords:
                record.value_pc

    @users('__system__','demo')
    @warmup
    deftest_write_mail(self):
        """Writerecordsinheritingfrom'mail.thread'(norecomputation)."""
        records=self.env['mail.performance.thread'].search([])
        self.assertEqual(len(records),5)

        withself.assertQueryCount(__system__=2,demo=2):
            records.write({'name':'X'})

    @users('__system__','demo')
    @warmup
    deftest_write_mail_with_recomputation(self):
        """Writerecordsinheritingfrom'mail.thread'(withrecomputation)."""
        records=self.env['mail.performance.thread'].search([])
        self.assertEqual(len(records),5)

        withself.assertQueryCount(__system__=2,demo=2):
            records.write({'value':42})

    @users('__system__','demo')
    @warmup
    deftest_write_mail_with_tracking(self):
        """Writerecordsinheritingfrom'mail.thread'(withfieldtracking)."""
        record=self.env['mail.performance.thread'].create({
            'name':'Test',
            'track':'Y',
            'value':40,
            'partner_id':self.res_partner_12.id,
        })

        withself.assertQueryCount(__system__=3,demo=3):
            record.track='X'

    @users('__system__','demo')
    @warmup
    deftest_create_mail(self):
        """Createrecordsinheritingfrom'mail.thread'(withoutfieldtracking)."""
        model=self.env['mail.performance.thread']

        withself.assertQueryCount(__system__=2,demo=2):
            model.with_context(tracking_disable=True).create({'name':'X'})

    @users('__system__','demo')
    @warmup
    deftest_create_mail_with_tracking(self):
        """Createrecordsinheritingfrom'mail.thread'(withfieldtracking)."""
        withself.assertQueryCount(__system__=8,demo=8):
            self.env['mail.performance.thread'].create({'name':'X'})

    @users('__system__','emp')
    @warmup
    deftest_create_mail_simple(self):
        withself.assertQueryCount(__system__=7,emp=7):
            self.env['mail.test.simple'].create({'name':'Test'})

    @users('__system__','emp')
    @warmup
    deftest_write_mail_simple(self):
        rec=self.env['mail.test.simple'].create({'name':'Test'})
        withself.assertQueryCount(__system__=1,emp=1):
            rec.write({
                'name':'Test2',
                'email_from':'test@test.com',
            })


@tagged('mail_performance','post_install','-at_install')
classTestMailAPIPerformance(BaseMailPerformance):

    defsetUp(self):
        super(TestMailAPIPerformance,self).setUp()
        self.customer=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'TestCustomer',
            'email':'customer.test@example.com',
        })
        self.user_test=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'PauletteTestouille',
            'login':'paul',
            'email':'user.test.paulette@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })

        self._init_mail_gateway()

        #automaticallyfollowactivities,forbackwardcompatibilityconcerningquerycount
        self.env.ref('mail.mt_activities').write({'default':True})

    def_create_test_records(self):
        self.test_record_full=self.env['mail.test.ticket'].with_context(self._quick_create_ctx).create({
            'name':'TestRecord',
            'customer_id':self.customer.id,
            'user_id':self.user_test.id,
            'email_from':'nopartner.test@example.com',
        })
        self.test_template_full=self.env['mail.template'].create({
            'name':'TestTemplate',
            'model_id':self.env['ir.model']._get('mail.test.ticket').id,
            'subject':'About${object.name}',
            'body_html':'<p>Hello${object.name}</p>',
            'email_from':'${object.user_id.email_formatted|safe}',
            'partner_to':'${object.customer_id.id}',
            'email_to':'${("%sCustomer<%s>"%(object.name,object.email_from))|safe}',
        })

    @users('__system__','emp')
    @warmup
    deftest_adv_activity(self):
        model=self.env['mail.test.activity']

        withself.assertQueryCount(__system__=7,emp=7):
            model.create({'name':'Test'})

    @users('__system__','emp')
    @warmup
    @mute_logger('flectra.models.unlink')
    deftest_adv_activity_full(self):
        record=self.env['mail.test.activity'].create({'name':'Test'})
        MailActivity=self.env['mail.activity'].with_context({
            'default_res_model':'mail.test.activity',
        })

        withself.assertQueryCount(__system__=6,emp=6):
            activity=MailActivity.create({
                'summary':'TestActivity',
                'res_id':record.id,
                'activity_type_id':self.env.ref('mail.mail_activity_data_todo').id,
            })
            #readactivity_typetonormalizecachebetweenenterpriseandcommunity
            #voipmodulereadactivity_typeduringcreateleadingtoonelessqueryinenterpriseonaction_feedback
            _category=activity.activity_type_id.category

        withself.assertQueryCount(__system__=18,emp=22): #tm17/21
            activity.action_feedback(feedback='ZizisseDone!')

    @users('__system__','emp')
    @warmup
    @mute_logger('flectra.models.unlink')
    deftest_adv_activity_mixin(self):
        record=self.env['mail.test.activity'].create({'name':'Test'})

        withself.assertQueryCount(__system__=8,emp=8):
            activity=record.action_start('TestStart')
            #readactivity_typetonormalizecachebetweenenterpriseandcommunity
            #voipmodulereadactivity_typeduringcreateleadingtoonelessqueryinenterpriseonaction_close
            _category=activity.activity_type_id.category

        record.write({'name':'Dupewrite'})

        withself.assertQueryCount(__system__=19,emp=22): #tm18/21
            record.action_close('Dupefeedback')

        self.assertEqual(record.activity_ids,self.env['mail.activity'])

    @users('__system__','emp')
    @warmup
    @mute_logger('flectra.models.unlink','flectra.tests','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer(self):
        self._create_test_records()
        test_record=self.env['mail.test.ticket'].browse(self.test_record_full.id)
        customer_id=self.customer.id
        withself.assertQueryCount(__system__=2,emp=2):
            composer=self.env['mail.compose.message'].with_context({
                'default_composition_mode':'comment',
                'default_model':test_record._name,
                'default_res_id':test_record.id,
            }).create({
                'body':'<p>TestBody</p>',
                'partner_ids':[(4,customer_id)],
            })

        withself.assertQueryCount(__system__=34,emp=41): #tm33/40
            composer.send_mail()

    @users('__system__','emp')
    @warmup
    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail')
    deftest_mail_composer_nodelete(self):
        self._create_test_records()
        test_record=self.env['mail.test.ticket'].browse(self.test_record_full.id)
        customer_id=self.customer.id
        withself.assertQueryCount(__system__=2,emp=2):
            composer=self.env['mail.compose.message'].with_context({
                'default_composition_mode':'comment',
                'default_model':test_record._name,
                'default_res_id':test_record.id,
                'mail_auto_delete':False,
            }).create({
                'body':'<p>TestBody</p>',
                'partner_ids':[(4,customer_id)],
            })

        withself.assertQueryCount(__system__=27,emp=34): #tm26/33
            composer.send_mail()

    @users('__system__','emp')
    @warmup
    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    deftest_mail_composer_w_template(self):
        self._create_test_records()
        test_record=self.env['mail.test.ticket'].browse(self.test_record_full.id)
        test_template=self.env['mail.template'].browse(self.test_template_full.id)
        withself.assertQueryCount(__system__=34,emp=36): #tm14/16
            composer=self.env['mail.compose.message'].with_context({
                'default_composition_mode':'comment',
                'default_model':test_record._name,
                'default_res_id':test_record.id,
                'default_template_id':test_template.id,
            }).create({})
            composer.onchange_template_id_wrapper()

        withself.assertQueryCount(__system__=34,emp=41): #tm33/40
            composer.send_mail()

        #removecreatedpartnertoensuretestsarethesameeachrun
        self.env['res.partner'].sudo().search([('email','=','nopartner.test@example.com')]).unlink()

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_message_assignation_email(self):
        self.user_test.write({'notification_type':'email'})
        record=self.env['mail.test.track'].create({'name':'Test'})
        withself.assertQueryCount(__system__=39,emp=40): #tm37/38
            record.write({
                'user_id':self.user_test.id,
            })

    @users('__system__','emp')
    @warmup
    deftest_message_assignation_inbox(self):
        record=self.env['mail.test.track'].create({'name':'Test'})
        withself.assertQueryCount(__system__=20,emp=23): #tm19/22
            record.write({
                'user_id':self.user_test.id,
            })

    @users('__system__','emp')
    @warmup
    deftest_message_log(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})

        withself.assertQueryCount(__system__=1,emp=1):
            record._message_log(
                body='<p>Test_message_log</p>',
                message_type='comment')

    @users('__system__','emp')
    @warmup
    deftest_message_log_with_post(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})

        withself.assertQueryCount(__system__=4,emp=7):
            record.message_post(
                body='<p>Testmessage_postaslog</p>',
                subtype_xmlid='mail.mt_note',
                message_type='comment')

    @users('__system__','emp')
    @warmup
    deftest_message_post_no_notification(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})

        withself.assertQueryCount(__system__=4,emp=7):
            record.message_post(
                body='<p>TestPostPerformancesbasic</p>',
                partner_ids=[],
                message_type='comment',
                subtype_xmlid='mail.mt_comment')

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_message_post_one_email_notification(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})

        withself.assertQueryCount(__system__=29,emp=32): #tm28/31
            record.message_post(
                body='<p>TestPostPerformanceswithanemailping</p>',
                partner_ids=self.customer.ids,
                message_type='comment',
                subtype_xmlid='mail.mt_comment')

    @users('__system__','emp')
    @warmup
    deftest_message_post_one_inbox_notification(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})

        withself.assertQueryCount(__system__=14,emp=19):
            record.message_post(
                body='<p>TestPostPerformanceswithaninboxping</p>',
                partner_ids=self.user_test.partner_id.ids,
                message_type='comment',
                subtype_xmlid='mail.mt_comment')

    @mute_logger('flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_message_subscribe_default(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})

        withself.assertQueryCount(__system__=6,emp=6):
            record.message_subscribe(partner_ids=self.user_test.partner_id.ids)

        withself.assertQueryCount(__system__=3,emp=3):
            record.message_subscribe(partner_ids=self.user_test.partner_id.ids)

    @mute_logger('flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_message_subscribe_subtypes(self):
        record=self.env['mail.test.simple'].create({'name':'Test'})
        subtype_ids=(self.env.ref('test_mail.st_mail_test_simple_external')|self.env.ref('mail.mt_comment')).ids

        withself.assertQueryCount(__system__=5,emp=5):
            record.message_subscribe(partner_ids=self.user_test.partner_id.ids,subtype_ids=subtype_ids)

        withself.assertQueryCount(__system__=2,emp=2):
            record.message_subscribe(partner_ids=self.user_test.partner_id.ids,subtype_ids=subtype_ids)

    @mute_logger('flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_message_track(self):
        record=self.env['mail.performance.tracking'].create({'name':'Zizizatestname'})
        withself.assertQueryCount(__system__=3,emp=3):
            record.write({'name':'Zizizanewtestname'})
            record.flush()

        withself.assertQueryCount(__system__=5,emp=5):
            record.write({'field_%s'%(i):'TrackedCharFields%s'%(i)foriinrange(3)})
            record.flush()

        withself.assertQueryCount(__system__=6,emp=6):
            record.write({'field_%s'%(i):'FieldWithoutCache%s'%(i)foriinrange(3)})
            record.flush()
            record.write({'field_%s'%(i):'FieldWithCache%s'%(i)foriinrange(3)})
            record.flush()

    @users('__system__','emp')
    @warmup
    deftest_notification_reply_to_batch(self):
        test_records_sudo=self.env['mail.test.container'].sudo().create([
            {'alias_name':'alias.test.%s.%d'%(self.env.user.name,index),
             'customer_id':self.customer.id,
             'name':'Test_%d'%index,
            }forindexinrange(10)
        ])

        withself.assertQueryCount(__system__=1,emp=1):
            test_records=self.env['mail.test.container'].browse(test_records_sudo.ids)
            reply_to=test_records._notify_get_reply_to(
                default=self.env.user.email_formatted
            )

        forrecordintest_records:
            self.assertEqual(
                reply_to[record.id],
                formataddr(
                    ("%s%s"%(self.env.user.company_id.name,record.name),
                     "%s@%s"%(record.alias_name,self.alias_domain)
                    )
                )
            )


@tagged('mail_performance','post_install','-at_install')
classTestMailComplexPerformance(BaseMailPerformance):

    defsetUp(self):
        super(TestMailComplexPerformance,self).setUp()
        self.user_portal=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'OliviaPortal',
            'login':'port',
            'email':'p.p@example.com',
            'signature':'--\nOlivia',
            'notification_type':'email',
            'groups_id':[(6,0,[self.env.ref('base.group_portal').id])],
        })
        self.admin=self.env.user

        self.channel=self.env['mail.channel'].with_context(self._quick_create_ctx).create({
            'name':'Listener',
        })

        #preparerecipientstotestformorerealisticworkload
        self.customer=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'TestCustomer',
            'email':'test@example.com'
        })
        self.container=self.env['mail.test.container'].with_context(mail_create_nosubscribe=True).create({
            'name':'TestContainer',
            'customer_id':self.customer.id,
            'alias_name':'test-alias',
        })
        Partners=self.env['res.partner'].with_context(self._quick_create_ctx)
        self.partners=self.env['res.partner']
        forxinrange(0,10):
            self.partners|=Partners.create({'name':'Test%s'%x,'email':'test%s@example.com'%x})
        self.container.message_subscribe(self.partners.ids,subtype_ids=[
            self.env.ref('mail.mt_comment').id,
            self.env.ref('test_mail.st_mail_test_container_child_full').id]
        )

        self._init_mail_gateway()

        #`test_complex_mail_mail_send`
        self.container.flush()

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_mail_mail_send(self):
        message=self.env['mail.message'].sudo().create({
            'subject':'Test',
            'body':'<p>Test</p>',
            'author_id':self.env.user.partner_id.id,
            'email_from':self.env.user.partner_id.email,
            'model':'mail.test.container',
            'res_id':self.container.id,
        })
        mail=self.env['mail.mail'].sudo().create({
            'body_html':'<p>Test</p>',
            'mail_message_id':message.id,
            'recipient_ids':[(4,pid)forpidinself.partners.ids],
        })
        mail_ids=mail.ids
        withself.assertQueryCount(__system__=7,emp=7):
            self.env['mail.mail'].sudo().browse(mail_ids).send()

        self.assertEqual(mail.body_html,'<p>Test</p>')
        self.assertEqual(mail.reply_to,formataddr(('%s%s'%(self.env.company.name,self.container.name),'test-alias@example.com')))

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_message_post(self):
        self.container.message_subscribe(self.user_portal.partner_id.ids)
        record=self.container.with_user(self.env.user)

        withself.assertQueryCount(__system__=64,emp=65): #tm63/64
            record.message_post(
                body='<p>TestPostPerformances</p>',
                message_type='comment',
                subtype_xmlid='mail.mt_comment')

        self.assertEqual(record.message_ids[0].body,'<p>TestPostPerformances</p>')
        self.assertEqual(record.message_ids[0].notified_partner_ids,self.partners|self.user_portal.partner_id)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_message_post_template(self):
        self.container.message_subscribe(self.user_portal.partner_id.ids)
        record=self.container.with_user(self.env.user)
        template_id=self.env.ref('test_mail.mail_test_container_tpl').id

        withself.assertQueryCount(__system__=78,emp=80): #tm73/75
            record.message_post_with_template(template_id,message_type='comment',composition_mode='comment')

        self.assertEqual(record.message_ids[0].body,'<p>Addingstuffon%s</p>'%record.name)
        self.assertEqual(record.message_ids[0].notified_partner_ids,self.partners|self.user_portal.partner_id|self.customer)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_message_subscribe(self):
        pids=self.partners.ids
        cids=self.channel.ids
        subtypes=self.env.ref('mail.mt_comment')|self.env.ref('test_mail.st_mail_test_ticket_container_upd')
        subtype_ids=subtypes.ids
        rec=self.env['mail.test.ticket'].create({
            'name':'Test',
            'container_id':False,
            'customer_id':False,
            'user_id':self.user_portal.id,
        })
        rec1=rec.with_context(active_test=False)     #toseeinactiverecords

        self.assertEqual(rec1.message_partner_ids,self.env.user.partner_id|self.user_portal.partner_id)
        self.assertEqual(rec1.message_channel_ids,self.env['mail.channel'])

        #subscribenewfollowerswithforcedgivensubtypes
        withself.assertQueryCount(__system__=8,emp=8):
            rec.message_subscribe(
                partner_ids=pids[:4],
                channel_ids=cids,
                subtype_ids=subtype_ids
            )

        self.assertEqual(rec1.message_partner_ids,self.env.user.partner_id|self.user_portal.partner_id|self.partners[:4])
        self.assertEqual(rec1.message_channel_ids,self.channel)

        #subscribeexistingandnewfollowerswithforce=False,meaningonlysomenewfollowerswillbeadded
        withself.assertQueryCount(__system__=6,emp=6):
            rec.message_subscribe(
                partner_ids=pids[:6],
                channel_ids=cids,
                subtype_ids=None
            )

        self.assertEqual(rec1.message_partner_ids,self.env.user.partner_id|self.user_portal.partner_id|self.partners[:6])
        self.assertEqual(rec1.message_channel_ids,self.channel)

        #subscribeexistingandnewfollowerswithforce=True,meaningallwillhavethesamesubtypes
        withself.assertQueryCount(__system__=7,emp=7):
            rec.message_subscribe(
                partner_ids=pids,
                channel_ids=cids,
                subtype_ids=subtype_ids
            )

        self.assertEqual(rec1.message_partner_ids,self.env.user.partner_id|self.user_portal.partner_id|self.partners)
        self.assertEqual(rec1.message_channel_ids,self.channel)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_tracking_assignation(self):
        """Assignationperformancetestonalready-createdrecord"""
        rec=self.env['mail.test.ticket'].create({
            'name':'Test',
            'container_id':self.container.id,
            'customer_id':self.customer.id,
            'user_id':self.env.uid,
        })
        rec1=rec.with_context(active_test=False)     #toseeinactiverecords
        self.assertEqual(rec1.message_partner_ids,self.partners|self.env.user.partner_id)
        withself.assertQueryCount(__system__=39,emp=40): #tm37/38
            rec.write({'user_id':self.user_portal.id})
        self.assertEqual(rec1.message_partner_ids,self.partners|self.env.user.partner_id|self.user_portal.partner_id)
        #writetrackingmessage
        self.assertEqual(rec1.message_ids[0].subtype_id,self.env.ref('mail.mt_note'))
        self.assertEqual(rec1.message_ids[0].notified_partner_ids,self.env['res.partner'])
        #creationmessage
        self.assertEqual(rec1.message_ids[1].subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))
        self.assertEqual(rec1.message_ids[1].notified_partner_ids,self.partners)
        self.assertEqual(len(rec1.message_ids),2)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_tracking_subscription_create(self):
        """Creationperformancetestinvolvingautosubscription,assignation,trackingwithsubtypeandtemplatesend."""
        container_id=self.container.id
        customer_id=self.customer.id
        user_id=self.user_portal.id

        withself.assertQueryCount(__system__=112,emp=113): #tm109/110
            rec=self.env['mail.test.ticket'].create({
                'name':'Test',
                'container_id':container_id,
                'customer_id':customer_id,
                'user_id':user_id,
            })

        rec1=rec.with_context(active_test=False)     #toseeinactiverecords
        self.assertEqual(rec1.message_partner_ids,self.partners|self.env.user.partner_id|self.user_portal.partner_id)
        #creationmessage
        self.assertEqual(rec1.message_ids[0].subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))
        self.assertEqual(rec1.message_ids[0].notified_partner_ids,self.partners|self.user_portal.partner_id)
        self.assertEqual(len(rec1.message_ids),1)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_tracking_subscription_subtype(self):
        """Writeperformancetestinvolvingautosubscription,trackingwithsubtype"""
        rec=self.env['mail.test.ticket'].create({
            'name':'Test',
            'container_id':False,
            'customer_id':False,
            'user_id':self.user_portal.id,
        })
        rec1=rec.with_context(active_test=False)     #toseeinactiverecords
        self.assertEqual(rec1.message_partner_ids,self.user_portal.partner_id|self.env.user.partner_id)
        self.assertEqual(len(rec1.message_ids),1)
        withself.assertQueryCount(__system__=79,emp=79): #tm78/78
            rec.write({
                'name':'Test2',
                'container_id':self.container.id,
            })

        self.assertEqual(rec1.message_partner_ids,self.partners|self.env.user.partner_id|self.user_portal.partner_id)
        #writetrackingmessage
        self.assertEqual(rec1.message_ids[0].subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))
        self.assertEqual(rec1.message_ids[0].notified_partner_ids,self.partners|self.user_portal.partner_id)
        #creationmessage
        self.assertEqual(rec1.message_ids[1].subtype_id,self.env.ref('mail.mt_note'))
        self.assertEqual(rec1.message_ids[1].notified_partner_ids,self.env['res.partner'])
        self.assertEqual(len(rec1.message_ids),2)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_tracking_subscription_write(self):
        """Writeperformancetestinvolvingautosubscription,trackingwithsubtypeandtemplatesend"""
        container_id=self.container.id
        customer_id=self.customer.id
        container2=self.env['mail.test.container'].with_context(mail_create_nosubscribe=True).create({
            'name':'TestContainer2',
            'customer_id':False,
            'alias_name':False,
        })

        rec=self.env['mail.test.ticket'].create({
            'name':'Test',
            'container_id':container2.id,
            'customer_id':False,
            'user_id':self.user_portal.id,
        })
        rec1=rec.with_context(active_test=False)     #toseeinactiverecords
        self.assertEqual(rec1.message_partner_ids,self.user_portal.partner_id|self.env.user.partner_id)

        withself.assertQueryCount(__system__=86,emp=86): #tm85/85
            rec.write({
                'name':'Test2',
                'container_id':container_id,
                'customer_id':customer_id,
            })

        self.assertEqual(rec1.message_partner_ids,self.partners|self.env.user.partner_id|self.user_portal.partner_id)
        #writetrackingmessage
        self.assertEqual(rec1.message_ids[0].subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))
        self.assertEqual(rec1.message_ids[0].notified_partner_ids,self.partners|self.user_portal.partner_id)
        #creationmessage
        self.assertEqual(rec1.message_ids[1].subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))
        self.assertEqual(rec1.message_ids[1].notified_partner_ids,self.user_portal.partner_id)
        self.assertEqual(len(rec1.message_ids),2)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('__system__','emp')
    @warmup
    deftest_complex_tracking_template(self):
        """Writeperformancetestinvolvingassignation,trackingwithtemplate"""
        customer_id=self.customer.id
        self.assertTrue(self.env.registry.ready,"Weneedtosimulatethatregisteryisready")
        rec=self.env['mail.test.ticket'].create({
            'name':'Test',
            'container_id':self.container.id,
            'customer_id':False,
            'user_id':self.user_portal.id,
            'mail_template':self.env.ref('test_mail.mail_test_ticket_tracking_tpl').id,
        })
        rec1=rec.with_context(active_test=False)     #toseeinactiverecords
        self.assertEqual(rec1.message_partner_ids,self.partners|self.env.user.partner_id|self.user_portal.partner_id)

        withself.assertQueryCount(__system__=31,emp=32): #tm29/30
            rec.write({
                'name':'Test2',
                'customer_id':customer_id,
                'user_id':self.env.uid,
            })

        #writetemplatemessage(senttocustomer,massmailingkeptforhistory)
        self.assertEqual(rec1.message_ids[0].subtype_id,self.env['mail.message.subtype'])
        self.assertEqual(rec1.message_ids[0].subject,'TestTemplate')
        #writetrackingmessage
        self.assertEqual(rec1.message_ids[1].subtype_id,self.env.ref('mail.mt_note'))
        self.assertEqual(rec1.message_ids[1].notified_partner_ids,self.env['res.partner'])
        #creationmessage
        self.assertEqual(rec1.message_ids[2].subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))
        self.assertEqual(rec1.message_ids[2].notified_partner_ids,self.partners|self.user_portal.partner_id)
        self.assertEqual(len(rec1.message_ids),3)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('emp')
    @warmup
    deftest_message_format(self):
        """Testperformanceof`_message_format`andof`message_format`with
        multiplemessageswithmultipleattachments,differentauthors,various
        notifications,anddifferenttrackingvalues.
        Thosemessagesmightnotmakesensefunctionallybuttheyarecraftedto
        coverasmuchofthecodeaspossibleinregardtonumberofqueries.
        """
        name_field=self.env['ir.model.fields']._get(self.container._name,'name')
        customer_id_field=self.env['ir.model.fields']._get(self.container._name,'customer_id')

        messages=self.env['mail.message'].sudo().create([{
            'subject':'Test0',
            'body':'<p>Test0</p>',
            'author_id':self.partners[0].id,
            'email_from':self.partners[0].email,
            'model':'mail.test.container',
            'res_id':self.container.id,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
            'attachment_ids':[
                (0,0,{
                    'name':'testfile0-%d'%j,
                    'datas':'data',
                })forjinrange(2)
            ],
            'notification_ids':[
                (0,0,{
                    'res_partner_id':self.partners[3].id,
                    'notification_type':'inbox',
                }),
                (0,0,{
                    'res_partner_id':self.partners[4].id,
                    'notification_type':'email',
                    'notification_status':'exception',
                }),
                (0,0,{
                    'res_partner_id':self.partners[6].id,
                    'notification_type':'email',
                    'notification_status':'exception',
                }),
            ],
            'tracking_value_ids':[
                (0,0,{
                    'field':name_field.id,
                    'field_desc':'Name',
                    'old_value_char':'old0',
                    'new_value_char':'new0',
                }),
                (0,0,{
                    'field':customer_id_field.id,
                    'field_desc':'Customer',
                    'old_value_integer':self.partners[7].id,
                    'new_value_integer':self.partners[8].id,
                }),
            ]
        },{
            'subject':'Test1',
            'body':'<p>Test1</p>',
            'author_id':self.partners[1].id,
            'email_from':self.partners[1].email,
            'model':'mail.test.container',
            'res_id':self.container.id,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'attachment_ids':[
                (0,0,{
                    'name':'testfile1-%d'%j,
                    'datas':'data',
                })forjinrange(2)
            ],
            'notification_ids':[
                (0,0,{
                    'res_partner_id':self.partners[5].id,
                    'notification_type':'inbox',
                }),
                (0,0,{
                    'res_partner_id':self.partners[6].id,
                    'notification_type':'email',
                    'notification_status':'exception',
                }),
            ],
            'tracking_value_ids':[
                (0,0,{
                    'field':name_field.id,
                    'field_desc':'Name',
                    'old_value_char':'old1',
                    'new_value_char':'new1',
                }),
                (0,0,{
                    'field':customer_id_field.id,
                    'field_desc':'Customer',
                    'old_value_integer':self.partners[7].id,
                    'new_value_integer':self.partners[8].id,
                }),
            ]
        }])

        withself.assertQueryCount(emp=6):
            res=messages.message_format()
            self.assertEqual(len(res),2)
            formessageinres:
                self.assertEqual(len(message['attachment_ids']),2)

        messages.flush()
        messages.invalidate_cache()

        withself.assertQueryCount(emp=18):
            res=messages.message_format()
            self.assertEqual(len(res),2)
            formessageinres:
                self.assertEqual(len(message['attachment_ids']),2)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('emp')
    @warmup
    deftest_message_format_group_thread_name_by_model(self):
        """Ensuresthefetchofmultiplethreadnamesisgroupedbymodel."""
        records=[]
        foriinrange(5):
            records.append(self.env['mail.test.simple'].create({'name':'Test'}))
        records.append(self.env['mail.test.track'].create({'name':'Test'}))

        messages=self.env['mail.message'].create([{
            'model':record._name,
            'res_id':record.id
        }forrecordinrecords])

        withself.assertQueryCount(emp=5):
            res=messages.message_format()
            self.assertEqual(len(res),6)

        messages.flush()
        messages.invalidate_cache()

        withself.assertQueryCount(emp=15):
            res=messages.message_format()
            self.assertEqual(len(res),6)


@tagged('mail_performance','post_install','-at_install')
classTestMailHeavyPerformancePost(BaseMailPerformance):

    defsetUp(self):
        super(TestMailHeavyPerformancePost,self).setUp()

        #record
        self.customer=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'customer',
            'email':'customer@example.com',
        })
        self.record=self.env['mail.test.container'].with_context(mail_create_nosubscribe=True).create({
            'name':'Testrecord',
            'customer_id':self.customer.id,
            'alias_name':'test-alias',
        })
        #followers
        self.user_follower_email=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'user_follower_email',
            'login':'user_follower_email',
            'email':'user_follower_email@example.com',
            'notification_type':'email',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })
        self.user_follower_inbox=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'user_follower_inbox',
            'login':'user_follower_inbox',
            'email':'user_follower_inbox@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })
        self.partner_follower=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'partner_follower',
            'email':'partner_follower@example.com',
        })
        self.record.message_subscribe([
            self.partner_follower.id,
            self.user_follower_inbox.partner_id.id,
            self.user_follower_email.partner_id.id
        ])

        #partner_ids
        self.user_inbox=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'user_inbox',
            'login':'user_inbox',
            'email':'user_inbox@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })
        self.user_email=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'user_email',
            'login':'user_email',
            'email':'user_email@example.com',
            'notification_type':'email',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })
        self.partner=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'partner',
            'email':'partner@example.com',
        })
        #channelsuser/partner
        self.partner_channel_inbox=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'partner_channel_inbox',
            'email':'partner_channel_inbox@example.com',
        })
        self.partner_channel_email=self.env['res.partner'].with_context(self._quick_create_ctx).create({
            'name':'partner_channel_email',
            'email':'partner_channel_email@example.com',
        })
        self.user_channel_inbox=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'user_channel_inbox',
            'login':'user_channel_inbox',
            'email':'user_channel_inbox@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })
        self.user_channel_email=self.env['res.users'].with_context(self._quick_create_ctx).create({
            'name':'user_channel_email',
            'login':'user_channel_email',
            'email':'user_channel_email@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[self.env.ref('base.group_user').id])],
        })
        #channels
        self.channel_inbox=self.env['mail.channel'].with_context(self._quick_create_ctx).create({
            'name':'channel_inbox',
            'channel_partner_ids':[(4,self.partner_channel_inbox.id),(4,self.user_channel_inbox.partner_id.id)]
        })
        self.channel_email=self.env['mail.channel'].with_context(self._quick_create_ctx).create({
            'name':'channel_email',
            'email_send':True,
            'channel_partner_ids':[(4,self.partner_channel_email.id),(4,self.user_channel_email.partner_id.id)]
        })
        self.vals=[{
            'datas':base64.b64encode(bytes("attachementcontent%s"%i,'utf-8')),
            'name':'fileText_test%s.txt'%i,
            'mimetype':'text/plain',
            'res_model':'mail.compose.message',
            'res_id':0,
        }foriinrange(3)]

        self._init_mail_gateway()

        self.patch(self.env.registry,'ready',True)

    @mute_logger('flectra.tests','flectra.addons.mail.models.mail_mail','flectra.models.unlink')
    @users('emp')
    @warmup
    deftest_complete_message_post(self):
        #aimstocoverasmuchfeaturesofmessage_postaspossible
        partner_ids=[self.user_inbox.partner_id.id,self.user_email.partner_id.id,self.partner.id]
        channel_ids=[self.channel_inbox.id,self.channel_email.id]
        record=self.record.with_user(self.env.user)
        attachements=[ #notlinearonnumberofattachements
            ('attachtuple1',"attachementtupplecontent1"),
            ('attachtuple2',"attachementtupplecontent2",{'cid':'cid1'}),
            ('attachtuple3',"attachementtupplecontent3",{'cid':'cid2'}),
        ]
        self.attachements=self.env['ir.attachment'].with_user(self.env.user).create(self.vals)
        attachement_ids=self.attachements.ids
        withself.assertQueryCount(emp=87): #tm80/com85
            self.cr.sql_log=self.warmandself.cr.sql_log_count
            record.with_context({}).message_post(
                body='<p>Testbody<imgsrc="cid:cid1"><imgsrc="cid:cid2"></p>',
                subject='TestSubject',
                message_type='notification',
                subtype_xmlid=None,
                partner_ids=partner_ids,
                channel_ids=channel_ids,
                parent_id=False,
                attachments=attachements,
                attachment_ids=attachement_ids,
                add_sign=True,
                model_description=False,
                mail_auto_delete=True
            )
            self.cr.sql_log=False
        self.assertTrue(record.message_ids[0].body.startswith('<p>Testbody<imgsrc="/web/image/'))
        self.assertEqual(self.attachements.mapped('res_model'),[record._nameforiinrange(3)])
        self.assertEqual(self.attachements.mapped('res_id'),[record.idforiinrange(3)])
        #self.assertEqual(record.message_ids[0].notified_partner_ids,[])
