#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime,timedelta
fromdateutil.relativedeltaimportrelativedelta
fromunittest.mockimportpatch
fromunittest.mockimportDEFAULT

importpytz

fromflectraimportfields,exceptions,tests
fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.addons.test_mail.models.test_mail_modelsimportMailTestActivity
fromflectra.toolsimportmute_logger
fromflectra.tests.commonimportForm


classTestActivityCommon(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestActivityCommon,cls).setUpClass()
        cls.test_record=cls.env['mail.test.activity'].with_context(cls._test_context).create({'name':'Test'})
        #resetctx
        cls._reset_mail_context(cls.test_record)


@tests.tagged('mail_activity')
classTestActivityRights(TestActivityCommon):

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_security_user_access_other(self):
        activity=self.test_record.with_user(self.user_employee).activity_schedule(
            'test_mail.mail_act_test_todo',
            user_id=self.user_admin.id)
        self.assertTrue(activity.can_write)
        activity.write({'user_id':self.user_employee.id})

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_security_user_access_own(self):
        activity=self.test_record.with_user(self.user_employee).activity_schedule(
            'test_mail.mail_act_test_todo')
        self.assertTrue(activity.can_write)
        activity.write({'user_id':self.user_admin.id})

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_security_user_noaccess_automated(self):
        def_employee_crash(*args,**kwargs):
            """Ifemployeeistestemployee,considerhehasnoaccessondocument"""
            recordset=args[0]
            ifrecordset.env.uid==self.user_employee.id:
                raiseexceptions.AccessError('HophophopErnest,pleasestepback.')
            returnDEFAULT

        withpatch.object(MailTestActivity,'check_access_rights',autospec=True,side_effect=_employee_crash):
            activity=self.test_record.activity_schedule(
                'test_mail.mail_act_test_todo',
                user_id=self.user_employee.id)

            activity2=self.test_record.activity_schedule('test_mail.mail_act_test_todo')
            activity2.write({'user_id':self.user_employee.id})

    deftest_activity_security_user_noaccess_manual(self):
        def_employee_crash(*args,**kwargs):
            """Ifemployeeistestemployee,considerhehasnoaccessondocument"""
            recordset=args[0]
            ifrecordset.env.uid==self.user_employee.id:
                raiseexceptions.AccessError('HophophopErnest,pleasestepback.')
            returnDEFAULT

        #cannotcreateactivitiesforpeoplethatcannotaccessrecord
        withpatch.object(MailTestActivity,'check_access_rights',autospec=True,side_effect=_employee_crash):
            withself.assertRaises(exceptions.UserError):
                activity=self.env['mail.activity'].create({
                    'activity_type_id':self.env.ref('test_mail.mail_act_test_todo').id,
                    'res_model_id':self.env.ref('test_mail.model_mail_test_activity').id,
                    'res_id':self.test_record.id,
                    'user_id':self.user_employee.id,
                })

        #cannotcreateactivitiesifnoaccesstothedocument
        withpatch.object(MailTestActivity,'check_access_rights',autospec=True,side_effect=_employee_crash):
            withself.assertRaises(exceptions.AccessError):
                activity=self.test_record.with_user(self.user_employee).activity_schedule(
                    'test_mail.mail_act_test_todo',
                    user_id=self.user_admin.id)


@tests.tagged('mail_activity')
classTestActivityFlow(TestActivityCommon):

    deftest_activity_flow_employee(self):
        withself.with_user('employee'):
            test_record=self.env['mail.test.activity'].browse(self.test_record.id)
            self.assertEqual(test_record.activity_ids,self.env['mail.activity'])

            #employeerecordanactivityandcheckthedeadline
            self.env['mail.activity'].create({
                'summary':'TestActivity',
                'date_deadline':date.today()+relativedelta(days=1),
                'activity_type_id':self.env.ref('mail.mail_activity_data_email').id,
                'res_model_id':self.env['ir.model']._get(test_record._name).id,
                'res_id':test_record.id,
            })
            self.assertEqual(test_record.activity_summary,'TestActivity')
            self.assertEqual(test_record.activity_state,'planned')

            test_record.activity_ids.write({'date_deadline':date.today()-relativedelta(days=1)})
            test_record.invalidate_cache() #TDEnote:shouldnothavetodoitIthink
            self.assertEqual(test_record.activity_state,'overdue')

            test_record.activity_ids.write({'date_deadline':date.today()})
            test_record.invalidate_cache() #TDEnote:shouldnothavetodoitIthink
            self.assertEqual(test_record.activity_state,'today')

            #activityisdone
            test_record.activity_ids.action_feedback(feedback='Somuchfeedback')
            self.assertEqual(test_record.activity_ids,self.env['mail.activity'])
            self.assertEqual(test_record.message_ids[0].subtype_id,self.env.ref('mail.mt_activities'))

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_notify_other_user(self):
        self.user_admin.notification_type='email'
        rec=self.test_record.with_user(self.user_employee)
        withself.assertSinglePostNotifications(
                [{'partner':self.partner_admin,'type':'email'}],
                message_info={'content':'assignedyouanactivity','subtype':'mail.mt_note','message_type':'user_notification'}):
            activity=rec.activity_schedule(
                'test_mail.mail_act_test_todo',
                user_id=self.user_admin.id)
        self.assertEqual(activity.create_uid,self.user_employee)
        self.assertEqual(activity.user_id,self.user_admin)

    deftest_activity_notify_same_user(self):
        self.user_employee.notification_type='email'
        rec=self.test_record.with_user(self.user_employee)
        withself.assertNoNotifications():
            activity=rec.activity_schedule(
                'test_mail.mail_act_test_todo',
                user_id=self.user_employee.id)
        self.assertEqual(activity.create_uid,self.user_employee)
        self.assertEqual(activity.user_id,self.user_employee)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_dont_notify_no_user_change(self):
        self.user_employee.notification_type='email'
        activity=self.test_record.activity_schedule('test_mail.mail_act_test_todo',user_id=self.user_employee.id)
        withself.assertNoNotifications():
            activity.with_user(self.user_admin).write({'user_id':self.user_employee.id})
        self.assertEqual(activity.user_id,self.user_employee)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_summary_sync(self):
        """Testsummaryfromtypeiscopiedonactivitiesifset(currentlyonlyinform-basedonchange)"""
        ActivityType=self.env['mail.activity.type']
        email_activity_type=ActivityType.create({
            'name':'email',
            'summary':'EmailSummary',
        })
        call_activity_type=ActivityType.create({'name':'call'})
        withForm(self.env['mail.activity'].with_context(default_res_model_id=self.env.ref('base.model_res_partner')))asActivityForm:
            ActivityForm.res_model_id=self.env.ref('base.model_res_partner')

            ActivityForm.activity_type_id=call_activity_type
            #activitysummaryshouldbeempty
            self.assertEqual(ActivityForm.summary,False)

            ActivityForm.activity_type_id=email_activity_type
            #activitysummaryshouldbereplacedwithemail'sdefaultsummary
            self.assertEqual(ActivityForm.summary,email_activity_type.summary)

            ActivityForm.activity_type_id=call_activity_type
            #activitysummaryremainsunchangedfromchangeofactivitytypeascallactivitydoesn'thavedefaultsummary
            self.assertEqual(ActivityForm.summary,email_activity_type.summary)

    deftest_action_feedback_attachment(self):
        Partner=self.env['res.partner']
        Activity=self.env['mail.activity']
        Attachment=self.env['ir.attachment']
        Message=self.env['mail.message']

        partner=self.env['res.partner'].create({
            'name':'Tester',
        })

        activity=Activity.create({
            'summary':'Test',
            'activity_type_id':1,
            'res_model_id':self.env.ref('base.model_res_partner').id,
            'res_id':partner.id,
        })

        attachments=Attachment
        attachments+=Attachment.create({
            'name':'test',
            'res_name':'test',
            'res_model':'mail.activity',
            'res_id':activity.id,
            'datas':'test',
        })
        attachments+=Attachment.create({
            'name':'test2',
            'res_name':'test',
            'res_model':'mail.activity',
            'res_id':activity.id,
            'datas':'testtest',
        })

        #Checkingiftheattachmenthasbeenforwardedtothemessage
        #whenmarkinganactivityas"Done"
        activity.action_feedback()
        activity_message=Message.search([],order='iddesc',limit=1)
        self.assertEqual(set(activity_message.attachment_ids.ids),set(attachments.ids))
        forattachmentinattachments:
            self.assertEqual(attachment.res_id,activity_message.id)
            self.assertEqual(attachment.res_model,activity_message._name)


@tests.tagged('mail_activity')
classTestActivityMixin(TestActivityCommon):

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_mixin(self):
        self.user_employee.tz=self.user_admin.tz
        withself.with_user('employee'):
            self.test_record=self.env['mail.test.activity'].browse(self.test_record.id)
            self.assertEqual(self.test_record.env.user,self.user_employee)

            now_utc=datetime.now(pytz.UTC)
            now_user=now_utc.astimezone(pytz.timezone(self.env.user.tzor'UTC'))
            today_user=now_user.date()

            #Testvariousschedulingofactivities
            act1=self.test_record.activity_schedule(
                'test_mail.mail_act_test_todo',
                today_user+relativedelta(days=1),
                user_id=self.user_admin.id)
            self.assertEqual(act1.automated,True)

            act_type=self.env.ref('test_mail.mail_act_test_todo')
            self.assertEqual(self.test_record.activity_summary,act_type.summary)
            self.assertEqual(self.test_record.activity_state,'planned')
            self.assertEqual(self.test_record.activity_user_id,self.user_admin)

            act2=self.test_record.activity_schedule(
                'test_mail.mail_act_test_meeting',
                today_user+relativedelta(days=-1))
            self.assertEqual(self.test_record.activity_state,'overdue')
            #`activity_user_id`isdefinedas`fields.Many2one('res.users','ResponsibleUser',related='activity_ids.user_id')`
            #itthereforereliesonthenaturalorderof`activity_ids`,accordingtowhichactivitycomesfirst.
            #Aswejustcreatedtheactivity,itsnotyetintherightorder.
            #Weforceitbyinvalidatingitsoitgetsfetchedfromdatabase,intherightorder.
            self.test_record.invalidate_cache(['activity_ids'])
            self.assertEqual(self.test_record.activity_user_id,self.user_employee)

            act3=self.test_record.activity_schedule(
                'test_mail.mail_act_test_todo',
                today_user+relativedelta(days=3),
                user_id=self.user_employee.id)
            self.assertEqual(self.test_record.activity_state,'overdue')
            #`activity_user_id`isdefinedas`fields.Many2one('res.users','ResponsibleUser',related='activity_ids.user_id')`
            #itthereforereliesonthenaturalorderof`activity_ids`,accordingtowhichactivitycomesfirst.
            #Aswejustcreatedtheactivity,itsnotyetintherightorder.
            #Weforceitbyinvalidatingitsoitgetsfetchedfromdatabase,intherightorder.
            self.test_record.invalidate_cache(['activity_ids'])
            self.assertEqual(self.test_record.activity_user_id,self.user_employee)

            self.test_record.invalidate_cache(ids=self.test_record.ids)
            self.assertEqual(self.test_record.activity_ids,act1|act2|act3)

            #Performtodoactivitiesforadmin
            self.test_record.activity_feedback(
                ['test_mail.mail_act_test_todo'],
                user_id=self.user_admin.id,
                feedback='Testfeedback',)
            self.assertEqual(self.test_record.activity_ids,act2|act3)

            #Rescheduleallactivities,shouldupdatetherecordstate
            self.assertEqual(self.test_record.activity_state,'overdue')
            self.test_record.activity_reschedule(
                ['test_mail.mail_act_test_meeting','test_mail.mail_act_test_todo'],
                date_deadline=today_user+relativedelta(days=3)
            )
            self.assertEqual(self.test_record.activity_state,'planned')

            #Performtodoactivitiesforremainingpeople
            self.test_record.activity_feedback(
                ['test_mail.mail_act_test_todo'],
                feedback='Testfeedback')

            #Settingactivitiesasdoneshoulddeletethemandpostmessages
            self.assertEqual(self.test_record.activity_ids,act2)
            self.assertEqual(len(self.test_record.message_ids),2)
            self.assertEqual(self.test_record.message_ids.mapped('subtype_id'),self.env.ref('mail.mt_activities'))

            #Performmeetingactivities
            self.test_record.activity_unlink(['test_mail.mail_act_test_meeting'])

            #Cancelingactivitiesshouldsimplyremovethem
            self.assertEqual(self.test_record.activity_ids,self.env['mail.activity'])
            self.assertEqual(len(self.test_record.message_ids),2)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_mixin_archive(self):
        rec=self.test_record.with_user(self.user_employee)
        new_act=rec.activity_schedule(
            'test_mail.mail_act_test_todo',
            user_id=self.user_admin.id)
        self.assertEqual(rec.activity_ids,new_act)
        rec.toggle_active()
        self.assertEqual(rec.active,False)
        self.assertEqual(rec.activity_ids,self.env['mail.activity'])
        rec.toggle_active()
        self.assertEqual(rec.active,True)
        self.assertEqual(rec.activity_ids,self.env['mail.activity'])

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_activity_mixin_reschedule_user(self):
        rec=self.test_record.with_user(self.user_employee)
        rec.activity_schedule(
            'test_mail.mail_act_test_todo',
            user_id=self.user_admin.id)
        self.assertEqual(rec.activity_ids[0].user_id,self.user_admin)

        #rescheduleitsownshouldnotalterother'sactivities
        rec.activity_reschedule(
            ['test_mail.mail_act_test_todo'],
            user_id=self.user_employee.id,
            new_user_id=self.user_employee.id)
        self.assertEqual(rec.activity_ids[0].user_id,self.user_admin)

        rec.activity_reschedule(
            ['test_mail.mail_act_test_todo'],
            user_id=self.user_admin.id,
            new_user_id=self.user_employee.id)
        self.assertEqual(rec.activity_ids[0].user_id,self.user_employee)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_my_activity_flow_employee(self):
        Activity=self.env['mail.activity']
        date_today=date.today()
        activity_1=Activity.create({
            'activity_type_id':self.env.ref('test_mail.mail_act_test_todo').id,
            'date_deadline':date_today,
            'res_model_id':self.env.ref('test_mail.model_mail_test_activity').id,
            'res_id':self.test_record.id,
            'user_id':self.user_admin.id,
        })
        activity_2=Activity.create({
            'activity_type_id':self.env.ref('test_mail.mail_act_test_call').id,
            'date_deadline':date_today+relativedelta(days=1),
            'res_model_id':self.env.ref('test_mail.model_mail_test_activity').id,
            'res_id':self.test_record.id,
            'user_id':self.user_employee.id,
        })

        test_record_1=self.env['mail.test.activity'].with_context(self._test_context).create({'name':'Test1'})
        activity_3=Activity.create({
            'activity_type_id':self.env.ref('test_mail.mail_act_test_todo').id,
            'date_deadline':date_today,
            'res_model_id':self.env.ref('test_mail.model_mail_test_activity').id,
            'res_id':test_record_1.id,
            'user_id':self.user_employee.id,
        })
        withself.with_user('employee'):
            record=self.env['mail.test.activity'].search([('my_activity_date_deadline','=',date_today)])
            self.assertEqual(test_record_1,record)

@tests.tagged('mail_activity')
classTestORM(TestActivityCommon):
    """Testforread_progress_bar"""

    deftest_week_grouping(self):
        """Thelabelsassociatedtoeachrecordinread_progress_barshouldmatch
        theonesfromread_group,eveninedgecaseslikeen_USlocaleonsundays
        """
        MailTestActivityCtx=self.env['mail.test.activity'].with_context({"lang":"en_US"})

        #Don'tmistakefieldsdateanddate_deadline:
        #*dateisjustarandomvalue
        #*date_deadlinedefinesactivity_state
        self.env['mail.test.activity'].create({
            'date':'2021-05-02',
            'name':"Yesterday,allmytroublesseemedsofaraway",
        }).activity_schedule(
            'test_mail.mail_act_test_todo',
            summary="Makeanothertestsuperasap(yesterday)",
            date_deadline=fields.Date.context_today(MailTestActivityCtx)-timedelta(days=7),
        )
        self.env['mail.test.activity'].create({
            'date':'2021-05-09',
            'name':"Thingswesaidtoday",
        }).activity_schedule(
            'test_mail.mail_act_test_todo',
            summary="Makeanothertestasap",
            date_deadline=fields.Date.context_today(MailTestActivityCtx),
        )
        self.env['mail.test.activity'].create({
            'date':'2021-05-16',
            'name':"TomorrowNeverKnows",
        }).activity_schedule(
            'test_mail.mail_act_test_todo',
            summary="Makeatesttomorrow",
            date_deadline=fields.Date.context_today(MailTestActivityCtx)+timedelta(days=7),
        )

        domain=[('date',"!=",False)]
        groupby="date:week"
        progress_bar={
            'field':'activity_state',
            'colors':{
                "overdue":'danger',
                "today":'warning',
                "planned":'success',
            }
        }

        #callread_grouptocomputegroupnames
        groups=MailTestActivityCtx.read_group(domain,fields=['date'],groupby=[groupby])
        progressbars=MailTestActivityCtx.read_progress_bar(domain,group_by=groupby,progress_bar=progress_bar)
        self.assertEqual(len(groups),3)
        self.assertEqual(len(progressbars),3)

        #formattheread_progress_barresulttogetadictionaryunderthis
        #format:{activity_state:group_name};theoriginalformat
        #(afterread_progress_bar)is{group_name:{activity_state:count}}
        pg_groups={
            next(stateforstate,countindata.items()ifcount):group_name
            forgroup_name,datainprogressbars.items()
        }

        self.assertEqual(groups[0][groupby],pg_groups["overdue"])
        self.assertEqual(groups[1][groupby],pg_groups["today"])
        self.assertEqual(groups[2][groupby],pg_groups["planned"])

