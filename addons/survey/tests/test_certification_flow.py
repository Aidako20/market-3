#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

fromflectra.addons.base.models.ir_mail_serverimportIrMailServer
fromflectra.addons.survey.testsimportcommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase


@tagged('-at_install','post_install','functional')
classTestCertificationFlow(common.TestSurveyCommon,HttpCase):

    deftest_flow_certification(self):
        #Step:surveyusercreatesthecertification
        #--------------------------------------------------
        withself.with_user('survey_user'):
            certification=self.env['survey.survey'].create({
                'title':'UserCertificationforSOlines',
                'access_mode':'public',
                'users_login_required':True,
                'questions_layout':'page_per_question',
                'users_can_go_back':True,
                'scoring_type':'scoring_with_answers',
                'scoring_success_min':85.0,
                'certification':True,
                'certification_mail_template_id':self.env.ref('survey.mail_template_certification').id,
                'is_time_limited':True,
                'time_limit':10,
                'state':'open',
            })

            q01=self._add_question(
                None,'Whendoyouknowit\'stherighttimetousetheSOlinemodel?','simple_choice',
                sequence=1,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=certification.id,
                labels=[
                    {'value':'Pleasestop'},
                    {'value':'OnlyontheSOform'},
                    {'value':'OnlyontheSurveyform'},
                    {'value':'Easy,allthetime!!!','is_correct':True,'answer_score':2.0}
                ])

            q02=self._add_question(
                None,'Onaverage,howmanylinesofcodedoyouneedwhenyouuseSOlinewidgets?','simple_choice',
                sequence=2,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=certification.id,
                labels=[
                    {'value':'1'},
                    {'value':'5','is_correct':True,'answer_score':2.0},
                    {'value':'100'},
                    {'value':'1000'}
                ])

            q03=self._add_question(
                None,'WhatdoyouthinkaboutSOlinewidgets(notrated)?','text_box',
                sequence=3,
                constr_mandatory=True,constr_error_msg='Pleasetelluswhatyouthink',survey_id=certification.id)

            q04=self._add_question(
                None,'Onascaleof1to10,howmuchdoyoulikeSOlinewidgets(notrated)?','simple_choice',
                sequence=4,
                constr_mandatory=True,constr_error_msg='Pleasetelluswhatyouthink',survey_id=certification.id,
                labels=[
                    {'value':'-1'},
                    {'value':'0'},
                    {'value':'100'}
                ])

            q05=self._add_question(
                None,'Selectallthecorrect"types"ofSOlines','multiple_choice',
                sequence=5,
                constr_mandatory=False,survey_id=certification.id,
                labels=[
                    {'value':'sale_order','is_correct':True,'answer_score':1.0},
                    {'value':'survey_page','is_correct':True,'answer_score':1.0},
                    {'value':'survey_question','is_correct':True,'answer_score':1.0},
                    {'value':'a_future_and_yet_unknown_model','is_correct':True,'answer_score':1.0},
                    {'value':'none','answer_score':-1.0}
                ])

        #Step:employeetakesthecertification
        #--------------------------------------------------
        self.authenticate('user_emp','user_emp')

        #Employeeopensstartpage
        response=self._access_start(certification)
        self.assertResponse(response,200,[certification.title,'Timelimitforthissurvey','10minutes'])

        #->thisshouldhavegeneratedanewuser_inputwithatoken
        user_inputs=self.env['survey.user_input'].search([('survey_id','=',certification.id)])
        self.assertEqual(len(user_inputs),1)
        self.assertEqual(user_inputs.partner_id,self.user_emp.partner_id)
        answer_token=user_inputs.access_token

        #Employeebeginssurveywithfirstpage
        response=self._access_page(certification,answer_token)
        self.assertResponse(response,200)
        csrf_token=self._find_csrf_token(response.text)

        r=self._access_begin(certification,answer_token)
        self.assertResponse(r,200)

        withpatch.object(IrMailServer,'connect'):
            self._answer_question(q01,q01.suggested_answer_ids.ids[3],answer_token,csrf_token)
            self._answer_question(q02,q02.suggested_answer_ids.ids[1],answer_token,csrf_token)
            self._answer_question(q03,"Ithinkthey'regreat!",answer_token,csrf_token)
            self._answer_question(q04,q04.suggested_answer_ids.ids[0],answer_token,csrf_token,button_submit='previous')
            self._answer_question(q03,"Justkidding,Idon'tlikeit...",answer_token,csrf_token)
            self._answer_question(q04,q04.suggested_answer_ids.ids[0],answer_token,csrf_token)
            self._answer_question(q05,[q05.suggested_answer_ids.ids[0],q05.suggested_answer_ids.ids[1],q05.suggested_answer_ids.ids[3]],answer_token,csrf_token)

        user_inputs.invalidate_cache()
        #Checkthatcertificationissuccessfullypassed
        self.assertEqual(user_inputs.scoring_percentage,87.5)
        self.assertTrue(user_inputs.scoring_success)

        #Checkthatthecertificationisstillsuccessfulevenifscoring_success_minofcertificationismodified
        certification.write({'scoring_success_min':90})
        self.assertTrue(user_inputs.scoring_success)

        #Checkanswercorrectionistakenintoaccount
        self.assertNotIn("Ithinkthey'regreat!",user_inputs.mapped('user_input_line_ids.value_text_box'))
        self.assertIn("Justkidding,Idon'tlikeit...",user_inputs.mapped('user_input_line_ids.value_text_box'))

        certification_email=self.env['mail.mail'].sudo().search([],limit=1,order="create_datedesc")
        #Checkcertificationemailcorrectlysentandcontainsdocument
        self.assertIn("UserCertificationforSOlines",certification_email.subject)
        self.assertIn("employee@example.com",certification_email.email_to)
        self.assertEqual(len(certification_email.attachment_ids),1)
        self.assertEqual(certification_email.attachment_ids[0].name,'CertificationDocument.html')

    deftest_randomized_certification(self):
        #Step:surveyusercreatestherandomizedcertification
        #--------------------------------------------------
        withself.with_user('survey_user'):
            certification=self.env['survey.survey'].create({
                'title':'UserrandomizedCertification',
                'questions_layout':'page_per_section',
                'questions_selection':'random',
                'state':'open',
                'scoring_type':'scoring_without_answers',
            })

            page1=self._add_question(
                None,'Page1',None,
                sequence=1,
                survey_id=certification.id,
                is_page=True,
                random_questions_count=1,
            )

            q101=self._add_question(
                None,'Whatistheanswertothefirstquestion?','simple_choice',
                sequence=2,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=certification.id,
                labels=[
                    {'value':'Thecorrectanswer','is_correct':True,'answer_score':1.0},
                    {'value':'Thewronganswer'},
                ])

            q102=self._add_question(
                None,'Whatistheanswertothesecondquestion?','simple_choice',
                sequence=3,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=certification.id,
                labels=[
                    {'value':'Thecorrectanswer','is_correct':True,'answer_score':1.0},
                    {'value':'Thewronganswer'},
                ])

        #Step:employeetakestherandomizedcertification
        #--------------------------------------------------
        self.authenticate('user_emp','user_emp')

        #Employeeopensstartpage
        response=self._access_start(certification)

        #->thisshouldhavegeneratedanewuser_inputwithatoken
        user_inputs=self.env['survey.user_input'].search([('survey_id','=',certification.id)])
        self.assertEqual(len(user_inputs),1)
        self.assertEqual(user_inputs.partner_id,self.user_emp.partner_id)
        answer_token=user_inputs.access_token

        #Employeebeginssurveywithfirstpage
        response=self._access_page(certification,answer_token)
        self.assertResponse(response,200)
        csrf_token=self._find_csrf_token(response.text)

        r=self._access_begin(certification,answer_token)
        self.assertResponse(r,200)

        withpatch.object(IrMailServer,'connect'):
            question_ids=user_inputs.predefined_question_ids
            self.assertEqual(len(question_ids),1,'Onlyonequestionshouldhavebeenselectedbytherandomization')
            #Whateverwhichquestionwasselected,thecorrectansweristhefirstone
            self._answer_question(question_ids,question_ids.suggested_answer_ids.ids[0],answer_token,csrf_token)

        statistics=user_inputs._prepare_statistics()
        self.assertEqual(statistics,[[
            {'text':'Correct','count':1},
            {'text':'Partially','count':0},
            {'text':'Incorrect','count':0},
            {'text':'Unanswered','count':0},
        ]],"Withtheconfiguredrandomization,thereshouldbeexactly1correctlyansweredquestionandnoneskipped.")
