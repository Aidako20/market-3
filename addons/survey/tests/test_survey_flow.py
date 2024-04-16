#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.survey.testsimportcommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase


@tagged('-at_install','post_install','functional')
classTestSurveyFlow(common.TestSurveyCommon,HttpCase):
    def_format_submission_data(self,page,answer_data,additional_post_data):
        post_data={}
        post_data['page_id']=page.id
        forquestion_id,answer_valsinanswer_data.items():
            question=page.question_ids.filtered(lambdaq:q.id==question_id)
            post_data.update(self._prepare_post_data(question,answer_vals['value'],post_data))
        post_data.update(**additional_post_data)
        returnpost_data

    deftest_flow_public(self):
        #Step:surveymanagercreatesthesurvey
        #--------------------------------------------------
        withself.with_user('survey_manager'):
            survey=self.env['survey.survey'].create({
                'title':'PublicSurveyforTarteAlDjotte',
                'access_mode':'public',
                'users_login_required':False,
                'questions_layout':'page_per_section',
                'state':'open'
            })

            #Firstpageisaboutcustomerdata
            page_0=self.env['survey.question'].create({
                'is_page':True,
                'sequence':1,
                'title':'Page1:YourData',
                'survey_id':survey.id,
            })
            page0_q0=self._add_question(
                page_0,'Whatisyourname','text_box',
                comments_allowed=False,
                constr_mandatory=True,constr_error_msg='Pleaseenteryourname',survey_id=survey.id)
            page0_q1=self._add_question(
                page_0,'Whatisyourage','numerical_box',
                comments_allowed=False,
                constr_mandatory=True,constr_error_msg='Pleaseenteryourname',survey_id=survey.id)

            #Secondpageisabouttartealdjotte
            page_1=self.env['survey.question'].create({
                'is_page':True,
                'sequence':4,
                'title':'Page2:TarteAlDjotte',
                'survey_id':survey.id,
            })
            page1_q0=self._add_question(
                page_1,'Whatdoyoulikemostinourtartealdjotte','multiple_choice',
                labels=[{'value':'Thegras'},
                        {'value':'Thebette'},
                        {'value':'Thetout'},
                        {'value':'Theregimeisfuckedup'}],survey_id=survey.id)

        #fetchstartingdatatocheckonlynewlycreateddataduringthisflow
        answers=self.env['survey.user_input'].search([('survey_id','=',survey.id)])
        answer_lines=self.env['survey.user_input.line'].search([('survey_id','=',survey.id)])
        self.assertEqual(answers,self.env['survey.user_input'])
        self.assertEqual(answer_lines,self.env['survey.user_input.line'])

        #Step:customertakesthesurvey
        #--------------------------------------------------

        #Customeropensstartpage
        r=self._access_start(survey)
        self.assertResponse(r,200,[survey.title])

        #->thisshouldhavegeneratedanewanswerwithatoken
        answers=self.env['survey.user_input'].search([('survey_id','=',survey.id)])
        self.assertEqual(len(answers),1)
        answer_token=answers.access_token
        self.assertTrue(answer_token)
        self.assertAnswer(answers,'new',self.env['survey.question'])

        #Customerbeginssurveywithfirstpage
        r=self._access_page(survey,answer_token)
        self.assertResponse(r,200)
        self.assertAnswer(answers,'new',self.env['survey.question'])
        csrf_token=self._find_csrf_token(r.text)

        r=self._access_begin(survey,answer_token)
        self.assertResponse(r,200)

        #Customersubmitfirstpageanswers
        answer_data={
            page0_q0.id:{'value':['AlfredPoilvache']},
            page0_q1.id:{'value':['44.0']},
        }
        post_data=self._format_submission_data(page_0,answer_data,{'csrf_token':csrf_token,'token':answer_token,'button_submit':'next'})
        r=self._access_submit(survey,answer_token,post_data)
        self.assertResponse(r,200)
        answers.invalidate_cache() #TDEnote:necessaryaslotsofsudoincontrollersmessingwithcache

        #->thisshouldhavegeneratedanswerlines
        self.assertAnswer(answers,'in_progress',page_0)
        self.assertAnswerLines(page_0,answers,answer_data)

        #Customerisredirectedonsecondpageandbeginsfillingit
        r=self._access_page(survey,answer_token)
        self.assertResponse(r,200)
        csrf_token=self._find_csrf_token(r.text)

        #Customersubmitsecondpageanswers
        answer_data={
            page1_q0.id:{'value':[page1_q0.suggested_answer_ids.ids[0],page1_q0.suggested_answer_ids.ids[1]]},
        }
        post_data=self._format_submission_data(page_1,answer_data,{'csrf_token':csrf_token,'token':answer_token,'button_submit':'next'})
        r=self._access_submit(survey,answer_token,post_data)
        self.assertResponse(r,200)
        answers.invalidate_cache() #TDEnote:necessaryaslotsofsudoincontrollersmessingwithcache

        #->thisshouldhavegeneratedanswerlinesandclosedtheanswer
        self.assertAnswer(answers,'done',page_1)
        self.assertAnswerLines(page_1,answers,answer_data)
