#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.toolsimportmute_logger


classTestInvite(TestMailCommon):

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_invite_email(self):
        test_record=self.env['mail.test.simple'].with_context(self._test_context).create({'name':'Test','email_from':'ignasse@example.com'})
        test_partner=self.env['res.partner'].with_context(self._test_context).create({
            'name':'ValidLelitre',
            'email':'valid.lelitre@agrolait.com'})

        mail_invite=self.env['mail.wizard.invite'].with_context({
            'default_res_model':'mail.test.simple',
            'default_res_id':test_record.id
        }).with_user(self.user_employee).create({
            'partner_ids':[(4,test_partner.id),(4,self.user_admin.partner_id.id)],
            'send_mail':True})
        withself.mock_mail_gateway():
            mail_invite.add_followers()

        #checkaddedfollowersandthatemailsweresent
        self.assertEqual(test_record.message_partner_ids,
                         test_partner|self.user_admin.partner_id)
        self.assertEqual(test_record.message_follower_ids.mapped('channel_id'),
                         self.env['mail.channel'])
        self.assertSentEmail(self.partner_employee,[test_partner])
        self.assertSentEmail(self.partner_employee,[self.partner_admin])
        self.assertEqual(len(self._mails),2)
