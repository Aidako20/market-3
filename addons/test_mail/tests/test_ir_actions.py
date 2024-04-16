#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.base.tests.test_ir_actionsimportTestServerActionsBase
fromflectra.addons.test_mail.tests.commonimportTestMailCommon


classTestServerActionsEmail(TestMailCommon,TestServerActionsBase):

    deftest_action_email(self):
        email_template=self._create_template('res.partner',{'partner_to':'%s'%self.test_partner.id})
        self.action.write({'state':'email','template_id':email_template.id})
        self.action.with_context(self.context).run()
        #checkanemailiswaitingforsending
        mail=self.env['mail.mail'].sudo().search([('subject','=','AboutTestingPartner')])
        self.assertEqual(len(mail),1)
        #checkemailcontent
        self.assertEqual(mail.body,'<p>HelloTestingPartner</p>')

    deftest_action_followers(self):
        self.test_partner.message_unsubscribe(self.test_partner.message_partner_ids.ids)
        random_partner=self.env['res.partner'].create({'name':'ThierryWololo'})
        self.action.write({
            'state':'followers',
            'partner_ids':[(4,self.env.ref('base.partner_admin').id),(4,random_partner.id)],
            'channel_ids':[(4,self.env.ref('mail.channel_all_employees').id)]
        })
        self.action.with_context(self.context).run()
        self.assertEqual(self.test_partner.message_partner_ids,self.env.ref('base.partner_admin')|random_partner)
        self.assertEqual(self.test_partner.message_channel_ids,self.env.ref('mail.channel_all_employees'))

    deftest_action_next_activity(self):
        self.action.write({
            'state':'next_activity',
            'activity_user_type':'specific',
            'activity_type_id':self.env.ref('mail.mail_activity_data_meeting').id,
            'activity_summary':'TestNew',
        })
        before_count=self.env['mail.activity'].search_count([])
        run_res=self.action.with_context(self.context).run()
        self.assertFalse(run_res,'ir_actions_server:createnextactivityactioncorrectlyfinishedshouldreturnFalse')
        self.assertEqual(self.env['mail.activity'].search_count([]),before_count+1)
        self.assertEqual(self.env['mail.activity'].search_count([('summary','=','TestNew')]),1)
