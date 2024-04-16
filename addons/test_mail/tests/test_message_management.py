#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


@tagged('mail_wizards')
classTestMailResend(TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailResend,cls).setUpClass()
        cls.test_record=cls.env['mail.test.simple'].with_context(cls._test_context).create({'name':'Test','email_from':'ignasse@example.com'})

        #Twousers
        cls.user1=mail_new_test_user(cls.env,login='e1',groups='base.group_public',name='Employee1',notification_type='email',email='e1') #invalidemail
        cls.user2=mail_new_test_user(cls.env,login='e2',groups='base.group_portal',name='Employee2',notification_type='email',email='e2@example.com')
        #Twopartner
        cls.partner1=cls.env['res.partner'].with_context(cls._test_context).create({
            'name':'Partner1',
            'email':'p1' #invalidemail
        })
        cls.partner2=cls.env['res.partner'].with_context(cls._test_context).create({
            'name':'Partner2',
            'email':'p2@example.com'
        })
        cls.partners=cls.env['res.partner'].concat(cls.user1.partner_id,cls.user2.partner_id,cls.partner1,cls.partner2)
        cls.invalid_email_partners=cls.env['res.partner'].concat(cls.user1.partner_id,cls.partner1)

    #@mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_mail_resend_workflow(self):
        withself.assertSinglePostNotifications(
                [{'partner':partner,'type':'email','status':'exception'}forpartnerinself.partners],
                message_info={'message_type':'notification'},
                sim_error='connect_failure'):
            message=self.test_record.with_user(self.user_admin).message_post(partner_ids=self.partners.ids,subtype_xmlid='mail.mt_comment',message_type='notification')

        wizard=self.env['mail.resend.message'].with_context({'mail_message_to_resend':message.id}).create({})
        self.assertEqual(wizard.notification_ids.mapped('res_partner_id'),self.partners,"wizardshouldmanagenotificationsforeachfailedpartner")

        #threemorefailuresentonbus,oneforeachmailinfailureandoneforresend
        self._reset_bus()
        withself.mock_mail_gateway(),self.assertBus([(self.cr.dbname,'res.partner',self.partner_admin.id)]*3):
            wizard.resend_mail_action()
        done_msgs,done_notifs=self.assertMailNotifications(message,[
            {'content':'','message_type':'notification',
             'notif':[{'partner':partner,'type':'email','status':'exception'ifpartnerinself.user1.partner_id|self.partner1else'sent'}forpartnerinself.partners]}]
        )
        self.assertEqual(wizard.notification_ids,done_notifs)
        self.assertEqual(done_msgs,message)

        self.user1.write({"email":'u1@example.com'})

        #twomorefailureupdatesentonbus,oneforfailedmailandoneforresend
        self._reset_bus()
        withself.mock_mail_gateway(),self.assertBus([(self.cr.dbname,'res.partner',self.partner_admin.id)]*2):
            self.env['mail.resend.message'].with_context({'mail_message_to_resend':message.id}).create({}).resend_mail_action()
        done_msgs,done_notifs=self.assertMailNotifications(message,[
            {'content':'','message_type':'notification',
             'notif':[{'partner':partner,'type':'email','status':'exception'ifpartner==self.partner1else'sent','check_send':partner==self.partner1}forpartnerinself.partners]}]
        )
        self.assertEqual(wizard.notification_ids,done_notifs)
        self.assertEqual(done_msgs,message)

        self.partner1.write({"email":'p1@example.com'})

        #Asuccessupdateshouldbesentonbusoncetheemailhasnomorefailure
        self._reset_bus()
        withself.mock_mail_gateway(),self.assertBus([(self.cr.dbname,'res.partner',self.partner_admin.id)]):
            self.env['mail.resend.message'].with_context({'mail_message_to_resend':message.id}).create({}).resend_mail_action()
        self.assertMailNotifications(message,[
            {'content':'','message_type':'notification',
             'notif':[{'partner':partner,'type':'email','status':'sent','check_send':partner==self.partner1}forpartnerinself.partners]}]
        )

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_remove_mail_become_canceled(self):
        #twofailuresentonbus,oneforeachmail
        self._reset_bus()
        withself.mock_mail_gateway(),self.assertBus([(self.cr.dbname,'res.partner',self.partner_admin.id)]*2):
            message=self.test_record.with_user(self.user_admin).message_post(partner_ids=self.partners.ids,subtype_xmlid='mail.mt_comment',message_type='notification')

        self.assertMailNotifications(message,[
            {'content':'','message_type':'notification',
             'notif':[{'partner':partner,'type':'email','status':'exception'ifpartnerinself.user1.partner_id|self.partner1else'sent'}forpartnerinself.partners]}]
        )

        wizard=self.env['mail.resend.message'].with_context({'mail_message_to_resend':message.id}).create({})
        partners=wizard.partner_ids.mapped("partner_id")
        self.assertEqual(self.invalid_email_partners,partners)
        wizard.partner_ids.filtered(lambdap:p.partner_id==self.partner1).write({"resend":False})
        wizard.resend_mail_action()

        self.assertMailNotifications(message,[
            {'content':'','message_type':'notification',
             'notif':[{'partner':partner,'type':'email',
                        'status':(partner==self.user1.partner_idand'exception')or(partner==self.partner1and'canceled')or'sent'}forpartnerinself.partners]}]
        )

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_cancel_all(self):
        self._reset_bus()
        withself.mock_mail_gateway(),self.assertBus([(self.cr.dbname,'res.partner',self.partner_admin.id)]*2):
            message=self.test_record.with_user(self.user_admin).message_post(partner_ids=self.partners.ids,subtype_xmlid='mail.mt_comment',message_type='notification')

        wizard=self.env['mail.resend.message'].with_context({'mail_message_to_resend':message.id}).create({})
        #oneupdateforcancell
        self._reset_bus()
        withself.mock_mail_gateway(),self.assertBus([(self.cr.dbname,'res.partner',self.partner_admin.id)]*1):
            wizard.cancel_mail_action()

        self.assertMailNotifications(message,[
            {'content':'','message_type':'notification',
             'notif':[{'partner':partner,'type':'email',
                        'check_send':partnerinself.user1.partner_id|self.partner1,
                        'status':'canceled'ifpartnerinself.user1.partner_id|self.partner1else'sent'}forpartnerinself.partners]}]
        )
