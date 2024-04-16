#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectra.addons.survey.testsimportcommon
fromflectra.exceptionsimportAccessError,UserError
fromflectra.testsimporttagged
fromflectra.tests.commonimportusers,HttpCase
fromflectra.toolsimportmute_logger


@tagged('security')
classTestAccess(common.TestSurveyCommon):

    defsetUp(self):
        super(TestAccess,self).setUp()

        self.answer_0=self._add_answer(self.survey,self.customer)
        self.answer_0_0=self._add_answer_line(self.question_ft,self.answer_0,'TestAnswer')
        self.answer_0_1=self._add_answer_line(self.question_num,self.answer_0,5)

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('user_emp')
    deftest_access_survey_employee(self):
        #Create:nope
        withself.assertRaises(AccessError):
            self.env['survey.survey'].create({'title':'TestSurvey2'})
        withself.assertRaises(AccessError):
            self.env['survey.question'].create({'title':'MyPage','sequence':0,'is_page':True,'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            self.env['survey.question'].create({'title':'MyQuestion','sequence':1,'page_id':self.page_0.id})

        #Read:nope
        withself.assertRaises(AccessError):
            self.env['survey.survey'].search([('title','ilike','Test')])
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).read(['title'])

        #Write:nope
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.page_0.with_user(self.env.user).write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.question_ft.with_user(self.env.user).write({'question':'NewTitle'})

        #Unlink:nope
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.page_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.question_ft.with_user(self.env.user).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('user_portal')
    deftest_access_survey_portal(self):
        #Create:nope
        withself.assertRaises(AccessError):
            self.env['survey.survey'].create({'title':'TestSurvey2'})
        withself.assertRaises(AccessError):
            self.env['survey.question'].create({'title':'MyPage','sequence':0,'is_page':True,'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            self.env['survey.question'].create({'title':'MyQuestion','sequence':1,'page_id':self.page_0.id})

        #Read:nope
        withself.assertRaises(AccessError):
            self.env['survey.survey'].search([('title','ilike','Test')])
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).read(['title'])

        #Write:nope
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.page_0.with_user(self.env.user).write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.question_ft.with_user(self.env.user).write({'question':'NewTitle'})

        #Unlink:nope
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.page_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.question_ft.with_user(self.env.user).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('user_public')
    deftest_access_survey_public(self):
        #Create:nope
        withself.assertRaises(AccessError):
            self.env['survey.survey'].create({'title':'TestSurvey2'})
        withself.assertRaises(AccessError):
            self.env['survey.question'].create({'title':'MyPage','sequence':0,'is_page':True,'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            self.env['survey.question'].create({'title':'MyQuestion','sequence':1,'page_id':self.page_0.id})

        #Read:nope
        withself.assertRaises(AccessError):
            self.env['survey.survey'].search([('title','ilike','Test')])
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).read(['title'])

        #Write:nope
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.page_0.with_user(self.env.user).write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.question_ft.with_user(self.env.user).write({'question':'NewTitle'})

        #Unlink:nope
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.page_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.question_ft.with_user(self.env.user).unlink()

    @users('survey_manager')
    deftest_access_survey_survey_manager(self):
        #Create:all
        survey=self.env['survey.survey'].create({'title':'TestSurvey2'})
        self.env['survey.question'].create({'title':'MyPage','sequence':0,'is_page':True,'survey_id':survey.id})
        self.env['survey.question'].create({'title':'MyQuestion','sequence':1,'survey_id':survey.id})

        #Read:all
        surveys=self.env['survey.survey'].search([('title','ilike','Test')])
        self.assertEqual(surveys,self.survey|survey)
        surveys.read(['title'])

        #Write:all
        (self.survey|survey).write({'title':'NewTitle'})

        #Unlink:all
        (self.survey|survey).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('survey_user')
    deftest_access_survey_survey_user(self):
        #Create:ownonly
        survey=self.env['survey.survey'].create({'title':'TestSurvey2'})
        self.env['survey.question'].create({'title':'MyPage','sequence':0,'is_page':True,'survey_id':survey.id})
        self.env['survey.question'].create({'title':'MyQuestion','sequence':1,'survey_id':survey.id})

        #Read:all
        surveys=self.env['survey.survey'].search([('title','ilike','Test')])
        self.assertEqual(surveys,self.survey|survey)
        surveys.read(['title'])

        #Write:ownonly
        survey.write({'title':'NewTitle'})
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).write({'title':'NewTitle'})

        #Unlink:ownonly
        survey.unlink()
        withself.assertRaises(AccessError):
            self.survey.with_user(self.env.user).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('user_emp')
    deftest_access_answers_employee(self):
        #Create:nope
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].create({'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].create({'question_id':self.question_num.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':self.answer_0.id})

        #Read:nope
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].search([('survey_id','in',[self.survey.id])])
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].search([('survey_id','in',[self.survey.id])])
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].browse(self.answer_0.ids).read(['state'])
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].browse(self.answer_0_0.ids).read(['value_numerical_box'])

        #Write:nope
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).write({'state':'done'})

        #Unlink:nope
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.answer_0_0.with_user(self.env.user).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('user_portal')
    deftest_access_answers_portal(self):
        #Create:nope
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].create({'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].create({'question_id':self.question_num.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':self.answer_0.id})

        #Read:nope
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].search([('survey_id','in',[self.survey.id])])
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].search([('survey_id','in',[self.survey.id])])
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].browse(self.answer_0.ids).read(['state'])
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].browse(self.answer_0_0.ids).read(['value_numerical_box'])

        #Write:nope
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).write({'state':'done'})

        #Unlink:nope
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.answer_0_0.with_user(self.env.user).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('user_public')
    deftest_access_answers_public(self):
        #Create:nope
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].create({'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].create({'question_id':self.question_num.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':self.answer_0.id})

        #Read:nope
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].search([('survey_id','in',[self.survey.id])])
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].search([('survey_id','in',[self.survey.id])])
        withself.assertRaises(AccessError):
            self.env['survey.user_input'].browse(self.answer_0.ids).read(['state'])
        withself.assertRaises(AccessError):
            self.env['survey.user_input.line'].browse(self.answer_0_0.ids).read(['value_numerical_box'])

        #Write:nope
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).write({'state':'done'})

        #Unlink:nope
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.answer_0_0.with_user(self.env.user).unlink()

    @mute_logger('flectra.addons.base.models.ir_model')
    @users('survey_user')
    deftest_access_answers_survey_user(self):
        survey_own=self.env['survey.survey'].create({'title':'Other'})
        self.env['survey.question'].create({'title':'Other','sequence':0,'is_page':True,'survey_id':survey_own.id})
        question_own=self.env['survey.question'].create({'title':'OtherQuestion','sequence':1,'survey_id':survey_own.id})

        #Create:ownsurveyonly
        answer_own=self.env['survey.user_input'].create({'survey_id':survey_own.id})
        answer_line_own=self.env['survey.user_input.line'].create({'question_id':question_own.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':answer_own.id})

        #Read:always
        answers=self.env['survey.user_input'].search([('survey_id','in',[survey_own.id,self.survey.id])])
        self.assertEqual(answers,answer_own|self.answer_0)

        answer_lines=self.env['survey.user_input.line'].search([('survey_id','in',[survey_own.id,self.survey.id])])
        self.assertEqual(answer_lines,answer_line_own|self.answer_0_0|self.answer_0_1)

        self.env['survey.user_input'].browse(answer_own.ids).read(['state'])
        self.env['survey.user_input'].browse(self.answer_0.ids).read(['state'])

        self.env['survey.user_input.line'].browse(answer_line_own.ids).read(['value_numerical_box'])
        self.env['survey.user_input.line'].browse(self.answer_0_0.ids).read(['value_numerical_box'])

        #Create:ownsurveyonly(movedafterreadbecauseDBnotcorrectlyrollbackedwithassertRaises)
        withself.assertRaises(AccessError):
            answer_other=self.env['survey.user_input'].create({'survey_id':self.survey.id})
        withself.assertRaises(AccessError):
            answer_line_other=self.env['survey.user_input.line'].create({'question_id':self.question_num.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':self.answer_0.id})

        #Write:ownsurveyonly
        answer_own.write({'state':'done'})
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).write({'state':'done'})

        #Unlink:ownsurveyonly
        answer_own.unlink()
        withself.assertRaises(AccessError):
            self.answer_0.with_user(self.env.user).unlink()
        withself.assertRaises(AccessError):
            self.answer_0_0.with_user(self.env.user).unlink()

    @users('survey_manager')
    deftest_access_answers_survey_manager(self):
        admin=self.env.ref('base.user_admin')
        withself.with_user(admin.login):
            survey_other=self.env['survey.survey'].create({'title':'Other'})
            self.env['survey.question'].create({'title':'Other','sequence':0,'is_page':True,'survey_id':survey_other.id})
            question_other=self.env['survey.question'].create({'title':'OtherQuestion','sequence':1,'survey_id':survey_other.id})
            self.assertEqual(survey_other.create_uid,admin)
            self.assertEqual(question_other.create_uid,admin)

        #Create:always
        answer_own=self.env['survey.user_input'].create({'survey_id':self.survey.id})
        answer_other=self.env['survey.user_input'].create({'survey_id':survey_other.id})
        answer_line_own=self.env['survey.user_input.line'].create({'question_id':self.question_num.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':answer_own.id})
        answer_line_other=self.env['survey.user_input.line'].create({'question_id':question_other.id,'answer_type':'numerical_box','value_numerical_box':3,'user_input_id':answer_other.id})

        #Read:always
        answers=self.env['survey.user_input'].search([('survey_id','in',[survey_other.id,self.survey.id])])
        self.assertEqual(answers,answer_own|answer_other|self.answer_0)

        answer_lines=self.env['survey.user_input.line'].search([('survey_id','in',[survey_other.id,self.survey.id])])
        self.assertEqual(answer_lines,answer_line_own|answer_line_other|self.answer_0_0|self.answer_0_1)

        self.env['survey.user_input'].browse(answer_own.ids).read(['state'])
        self.env['survey.user_input'].browse(self.answer_0.ids).read(['state'])

        self.env['survey.user_input.line'].browse(answer_line_own.ids).read(['value_numerical_box'])
        self.env['survey.user_input.line'].browse(self.answer_0_0.ids).read(['value_numerical_box'])

        #Write:always
        answer_own.write({'state':'done'})
        answer_other.write({'partner_id':self.env.user.partner_id.id})

        #Unlink:always
        (answer_own|answer_other|self.answer_0).unlink()


@tagged('post_install','-at_install')
classTestSurveySecurityControllers(common.TestSurveyCommon,HttpCase):
    deftest_survey_start_short(self):
        #avoidnameclashwithexistingdata
        surveys=self.env['survey.survey'].search([
            ('state','=','open'),
            ('session_state','in',['ready','in_progress'])
        ])
        surveys.write({'state':'done'})
        self.survey.write({
            'state':'open',
            'session_state':'ready',
            'session_code':'123456',
            'session_start_time':datetime.datetime.now(),
            'access_mode':'public',
            'users_login_required':False,
        })

        #rightshortaccesstoken
        response=self.url_open(f'/s/123456')
        self.assertEqual(response.status_code,200)
        self.assertIn('Thesessionwillbeginautomaticallywhenthehoststarts',response.text)

        #`like`operatorinjection
        response=self.url_open(f'/s/______')
        self.assertFalse(self.survey.titleinresponse.text)

        #rightshorttoken,butwrongstate
        self.survey.state='draft'
        response=self.url_open(f'/s/123456')
        self.assertFalse(self.survey.titleinresponse.text)

        #rightshorttoken,butwrong`session_state`
        self.survey.write({'state':'open','session_state':False})
        response=self.url_open(f'/s/123456')
        self.assertFalse(self.survey.titleinresponse.text)
