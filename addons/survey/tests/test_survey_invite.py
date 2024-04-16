#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields
fromflectra.addons.survey.testsimportcommon
fromflectra.exceptionsimportUserError
fromflectra.testsimportForm
fromflectra.tests.commonimportusers


classTestSurveyInvite(common.TestSurveyCommon):

    defsetUp(self):
        res=super(TestSurveyInvite,self).setUp()
        #bydefaultsignupnotallowed
        self.env["ir.config_parameter"].set_param('auth_signup.invitation_scope','b2b')
        returnres

    @users('survey_manager')
    deftest_survey_invite_action(self):
        #Checkcorrectlyconfiguredsurveyreturnsaninvitewizardaction
        action=self.survey.action_send_survey()
        self.assertEqual(action['res_model'],'survey.invite')

        #Badcases
        surveys=[
            #nopage
            self.env['survey.survey'].create({'title':'Testsurvey'}),
            #noquestions
            self.env['survey.survey'].create({'title':'Testsurvey','question_and_page_ids':[(0,0,{'is_page':True,'title':'P0','sequence':1})]}),
            #closed
            self.env['survey.survey'].with_user(self.survey_manager).create({
                'title':'S0',
                'state':'closed',
                'question_and_page_ids':[
                    (0,0,{'is_page':True,'title':'P0','sequence':1}),
                    (0,0,{'title':'Q0','sequence':2,'question_type':'text_box'})
                ]
            })
        ]
        forsurveyinsurveys:
            withself.assertRaises(UserError):
                survey.action_send_survey()

    @users('survey_manager')
    deftest_survey_invite(self):
        Answer=self.env['survey.user_input']
        deadline=fields.Datetime.now()+relativedelta(months=1)

        self.survey.write({'access_mode':'public','users_login_required':False})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))

        #somelowlevelchecksthatactioniscorrectlyconfigured
        self.assertEqual(Answer.search([('survey_id','=',self.survey.id)]),self.env['survey.user_input'])
        self.assertEqual(invite_form.survey_id,self.survey)

        invite_form.partner_ids.add(self.customer)
        invite_form.deadline=fields.Datetime.to_string(deadline)

        invite=invite_form.save()
        invite.action_invite()

        answers=Answer.search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),1)
        self.assertEqual(
            set(answers.mapped('email')),
            set([self.customer.email]))
        self.assertEqual(answers.mapped('partner_id'),self.customer)
        self.assertEqual(set(answers.mapped('deadline')),set([deadline]))

        withself.subTest('Warningwheninvitinganalreadyinvitedpartner'):
            action=self.survey.action_send_survey()
            invite_form=Form(self.env[action['res_model']].with_context(action['context']))
            invite_form.partner_ids.add(self.customer)

            self.assertIn(self.customer,invite_form.existing_partner_ids)
            self.assertEqual(invite_form.existing_text,
                             'Thefollowingcustomershavealreadyreceivedaninvite:CarolineCustomer.')


    @users('survey_manager')
    deftest_survey_invite_authentication_nosignup(self):
        Answer=self.env['survey.user_input']

        self.survey.write({'access_mode':'public','users_login_required':True})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))

        withself.assertRaises(UserError): #donotallowtoaddcustomer(partnerwithoutuser)
            invite_form.partner_ids.add(self.customer)
        invite_form.partner_ids.clear()
        invite_form.partner_ids.add(self.user_portal.partner_id)
        invite_form.partner_ids.add(self.user_emp.partner_id)
        withself.assertRaises(UserError):
            invite_form.emails='test1@example.com,RaouletteVignolette<test2@example.com>'
        invite_form.emails=False

        invite=invite_form.save()
        invite.action_invite()

        answers=Answer.search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),2)
        self.assertEqual(
            set(answers.mapped('email')),
            set([self.user_emp.email,self.user_portal.email]))
        self.assertEqual(answers.mapped('partner_id'),self.user_emp.partner_id|self.user_portal.partner_id)

    @users('survey_manager')
    deftest_survey_invite_authentication_signup(self):
        self.env["ir.config_parameter"].sudo().set_param('auth_signup.invitation_scope','b2c')
        self.survey.invalidate_cache()
        Answer=self.env['survey.user_input']

        self.survey.write({'access_mode':'public','users_login_required':True})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))

        invite_form.partner_ids.add(self.customer)
        invite_form.partner_ids.add(self.user_portal.partner_id)
        invite_form.partner_ids.add(self.user_emp.partner_id)
        #TDEFIXME:notsureforemailsinauthentication+signup
        #invite_form.emails='test1@example.com,RaouletteVignolette<test2@example.com>'

        invite=invite_form.save()
        invite.action_invite()

        answers=Answer.search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),3)
        self.assertEqual(
            set(answers.mapped('email')),
            set([self.customer.email,self.user_emp.email,self.user_portal.email]))
        self.assertEqual(answers.mapped('partner_id'),self.customer|self.user_emp.partner_id|self.user_portal.partner_id)

    @users('survey_manager')
    deftest_survey_invite_public(self):
        Answer=self.env['survey.user_input']

        self.survey.write({'access_mode':'public','users_login_required':False})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))

        invite_form.partner_ids.add(self.customer)
        invite_form.emails='test1@example.com,RaouletteVignolette<test2@example.com>'

        invite=invite_form.save()
        invite.action_invite()

        answers=Answer.search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),3)
        self.assertEqual(
            set(answers.mapped('email')),
            set(['test1@example.com','"RaouletteVignolette"<test2@example.com>',self.customer.email]))
        self.assertEqual(answers.mapped('partner_id'),self.customer)

    @users('survey_manager')
    deftest_survey_invite_token(self):
        Answer=self.env['survey.user_input']

        self.survey.write({'access_mode':'token','users_login_required':False})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))

        invite_form.partner_ids.add(self.customer)
        invite_form.emails='test1@example.com,RaouletteVignolette<test2@example.com>'

        invite=invite_form.save()
        invite.action_invite()

        answers=Answer.search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),3)
        self.assertEqual(
            set(answers.mapped('email')),
            set(['test1@example.com','"RaouletteVignolette"<test2@example.com>',self.customer.email]))
        self.assertEqual(answers.mapped('partner_id'),self.customer)

    @users('survey_manager')
    deftest_survey_invite_token_internal(self):
        Answer=self.env['survey.user_input']

        self.survey.write({'access_mode':'token','users_login_required':True})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))

        withself.assertRaises(UserError): #donotallowtoaddcustomer(partnerwithoutuser)
            invite_form.partner_ids.add(self.customer)
        withself.assertRaises(UserError): #donotallowtoaddportaluser
            invite_form.partner_ids.add(self.user_portal.partner_id)
        invite_form.partner_ids.clear()
        invite_form.partner_ids.add(self.user_emp.partner_id)
        withself.assertRaises(UserError):
            invite_form.emails='test1@example.com,RaouletteVignolette<test2@example.com>'
        invite_form.emails=False

        invite=invite_form.save()
        invite.action_invite()

        answers=Answer.search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),1)
        self.assertEqual(
            set(answers.mapped('email')),
            set([self.user_emp.email]))
        self.assertEqual(answers.mapped('partner_id'),self.user_emp.partner_id)

    deftest_survey_invite_token_by_email_nosignup(self):
        """
        Case:havemultiplespartnerswiththesameemailaddress
        IfIsetoneemailaddress,Iexpectoneemailtobesent
        """

        first_partner=self.env['res.partner'].create({
            'name':'Test1',
            'email':'test@example.com',
        })

        self.env['res.partner'].create({
            'name':'Test2',
            'email':'"RaoulPoilvache"<TEST@example.COM>',
        })

        self.survey.write({'access_mode':'token','users_login_required':False})
        action=self.survey.action_send_survey()
        invite_form=Form(self.env[action['res_model']].with_context(action['context']))
        invite_form.emails='test@example.com'
        invite=invite_form.save()
        invite.action_invite()

        answers=self.env['survey.user_input'].search([('survey_id','=',self.survey.id)])
        self.assertEqual(len(answers),1)
        self.assertEqual(answers.partner_id.display_name,first_partner.display_name)
