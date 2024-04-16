#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.survey.testsimportcommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase


@tagged('-at_install','post_install','functional')
classTestSurveyFlowWithConditions(common.TestSurveyCommon,HttpCase):
    deftest_conditional_flow_with_scoring(self):
        withself.with_user('survey_user'):
            survey=self.env['survey.survey'].create({
                'title':'Survey',
                'access_mode':'public',
                'questions_layout':'page_per_section',
                'scoring_type':'scoring_with_answers',
                'scoring_success_min':85.0,
                'state':'open',
            })

            page_0=self.env['survey.question'].with_user(self.survey_manager).create({
                'title':'Firstpage',
                'survey_id':survey.id,
                'sequence':1,
                'is_page':True,
            })

            q01=self._add_question(
                page_0,'Question1','simple_choice',
                sequence=1,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=survey.id,
                labels=[
                    {'value':'Answer1'},
                    {'value':'Answer2'},
                    {'value':'Answer3'},
                    {'value':'Answer4','is_correct':True,'answer_score':1.0}
                ])

            q02=self._add_question(
                page_0,'Question2','simple_choice',
                sequence=2,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=survey.id,
                is_conditional=True,triggering_question_id=q01.id,triggering_answer_id=q01.suggested_answer_ids.filtered(lambdaq:q.is_correct).id,
                labels=[
                    {'value':'Answer1'},
                    {'value':'Answer2','is_correct':True,'answer_score':1.0},
                    {'value':'Answer3'},
                    {'value':'Answer4'}
                ])

            q03=self._add_question(
                page_0,'Question3','simple_choice',
                sequence=1,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=survey.id,
                labels=[
                    {'value':'Answer1'},
                    {'value':'Answer2'},
                    {'value':'Answer3'},
                    {'value':'Answer4','is_correct':True,'answer_score':1.0}
                ])

            q04=self._add_question(
                page_0,'Question4','simple_choice',
                sequence=2,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=survey.id,
                is_conditional=True,triggering_question_id=q03.id,triggering_answer_id=q03.suggested_answer_ids.filtered(lambdaq:q.is_correct).id,
                labels=[
                    {'value':'Answer1'},
                    {'value':'Answer2','is_correct':True,'answer_score':1.0},
                    {'value':'Answer3'},
                    {'value':'Answer4'}
                ])

            q05=self._add_question(
                page_0,'Question5','simple_choice',
                sequence=1,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=survey.id,
                labels=[
                    {'value':'Answer1'},
                    {'value':'Answer2'},
                    {'value':'Answer3'},
                    {'value':'Answer4','is_correct':True,'answer_score':1.0}
                ])

            q06=self._add_question(
                page_0,'Question6','simple_choice',
                sequence=2,
                constr_mandatory=True,constr_error_msg='Pleaseselectananswer',survey_id=survey.id,
                is_conditional=True,triggering_question_id=q05.id,triggering_answer_id=q05.suggested_answer_ids.filtered(lambdaq:q.is_correct).id,
                labels=[
                    {'value':'Answer1'},
                    {'value':'Answer2','is_correct':True,'answer_score':1.0},
                    {'value':'Answer3'},
                    {'value':'Answer4'}
                ])

        #Useropensstartpage
        self._access_start(survey)

        #->thisshouldhavegeneratedanewuser_inputwithatoken
        user_inputs=self.env['survey.user_input'].search([('survey_id','=',survey.id)])
        self.assertEqual(len(user_inputs),1)
        answer_token=user_inputs.access_token

        #Userbeginssurveywithfirstpage
        response=self._access_page(survey,answer_token)
        self.assertResponse(response,200)
        csrf_token=self._find_csrf_token(response.text)

        r=self._access_begin(survey,answer_token)
        self.assertResponse(r,200)

        answers={
            q01:q01.suggested_answer_ids[3], #Right
            q02:q02.suggested_answer_ids[1], #Right
            q03:q03.suggested_answer_ids[0], #Wrong
            q05:q05.suggested_answer_ids[3], #Right
            q06:q06.suggested_answer_ids[2], #Wrong
        }

        self._answer_page(page_0,answers,answer_token,csrf_token)

        user_inputs.invalidate_cache()
        self.assertEqual(round(user_inputs.scoring_percentage),60,"Threerightanswersoutoffive(thefourthoneisstillhidden)")
        self.assertFalse(user_inputs.scoring_success)
