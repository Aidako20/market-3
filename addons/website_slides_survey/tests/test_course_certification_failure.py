#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.survey.tests.commonimportTestSurveyCommon


classTestCourseCertificationFailureFlow(TestSurveyCommon):
    deftest_course_certification_failure_flow(self):
        #Step1:createasimplecertification
        #--------------------------------------------------
        withself.with_user('survey_user'):
            certification=self.env['survey.survey'].create({
                'title':'Smallcoursecertification',
                'access_mode':'public',
                'users_login_required':True,
                'scoring_type':'scoring_with_answers',
                'certification':True,
                'is_attempts_limited':True,
                'scoring_success_min':100.0,
                'attempts_limit':2,
                'state':'open',
            })

            self._add_question(
                None,'Question1','simple_choice',
                sequence=1,
                survey_id=certification.id,
                labels=[
                    {'value':'Wronganswer'},
                    {'value':'Correctanswer','is_correct':True,'answer_score':1.0}
                ])

            self._add_question(
                None,'Question2','simple_choice',
                sequence=2,
                survey_id=certification.id,
                labels=[
                    {'value':'Wronganswer'},
                    {'value':'Correctanswer','is_correct':True,'answer_score':1.0}
                ])

        #Step1.1:createasimplechannel
        self.channel=self.env['slide.channel'].sudo().create({
            'name':'TestChannel',
            'channel_type':'training',
            'enroll':'public',
            'visibility':'public',
            'is_published':True,
        })

        #Step2:linkthecertificationtoaslideoftype'certification'
        self.slide_certification=self.env['slide.slide'].sudo().create({
            'name':'Certificationslide',
            'channel_id':self.channel.id,
            'slide_type':'certification',
            'survey_id':certification.id,
            'is_published':True,
        })
        #Step3:addpublicuserasmemberofthechannel
        self.channel._action_add_members(self.user_public.partner_id)
        #forcesrecomputeofpartner_idsaswecreatedirectlyinrelation
        self.channel.invalidate_cache()
        slide_partner=self.slide_certification._action_set_viewed(self.user_public.partner_id)
        self.slide_certification.with_user(self.user_public)._generate_certification_url()

        self.assertEqual(1,len(slide_partner.user_input_ids),'Auserinputshouldhavebeenautomaticallycreateduponslideview')

        #Step4:fillinthecreateduser_inputwithwronganswers
        self.fill_in_answer(slide_partner.user_input_ids[0],certification.question_ids)

        self.assertFalse(slide_partner.survey_scoring_success,'Quizzshouldnotbemarkedaspassedwithwronganswers')
        #forcesrecomputeofpartner_idsaswedeletedirectlyinrelation
        self.channel.invalidate_cache()
        self.assertIn(self.user_public.partner_id,self.channel.partner_ids,'Publicusershouldstillbeamemberofthecoursebecausehestillhasattemptsleft')

        #Step5:simulatea'retry'
        retry_user_input=self.slide_certification.survey_id.sudo()._create_answer(
            partner=self.user_public.partner_id,
            **{
                'slide_id':self.slide_certification.id,
                'slide_partner_id':slide_partner.id
            },
            invite_token=slide_partner.user_input_ids[0].invite_token
        )
        #Step6:fillinthenewuser_inputwithwronganswersagain
        self.fill_in_answer(retry_user_input,certification.question_ids)
        #forcesrecomputeofpartner_idsaswedeletedirectlyinrelation
        self.channel.invalidate_cache()
        self.assertNotIn(self.user_public.partner_id,self.channel.partner_ids,'Publicusershouldhavebeenkickedoutofthecoursebecausehefailedhislastattempt')

        #Step7:addpublicuserasmemberofthechannelonceagain
        self.channel._action_add_members(self.user_public.partner_id)
        #forcesrecomputeofpartner_idsaswecreatedirectlyinrelation
        self.channel.invalidate_cache()

        self.assertIn(self.user_public.partner_id,self.channel.partner_ids,'Publicusershouldbeamemberofthecourseonceagain')
        new_slide_partner=self.slide_certification._action_set_viewed(self.user_public.partner_id)
        self.slide_certification.with_user(self.user_public)._generate_certification_url()
        self.assertEqual(1,len(new_slide_partner.user_input_ids.filtered(lambdauser_input:user_input.state!='done')),'Anewuserinputshouldhavebeenautomaticallycreateduponslideview')

        #Step8:fillinthecreateduser_inputwithcorrectanswersthistime
        self.fill_in_answer(new_slide_partner.user_input_ids.filtered(lambdauser_input:user_input.state!='done')[0],certification.question_ids,good_answers=True)
        self.assertTrue(new_slide_partner.survey_scoring_success,'Quizzshouldbemarkedaspassedwithcorrectanswers')
        #forcesrecomputeofpartner_idsaswedeletedirectlyinrelation
        self.channel.invalidate_cache()
        self.assertIn(self.user_public.partner_id,self.channel.partner_ids,'Publicusershouldstillbeamemberofthecourse')

    deffill_in_answer(self,answer,questions,good_answers=False):
        """Fillsintheuser_inputwithanswersforallgivenquestions.
        Youcancontrolwhethertheanswerwillbecorrectornotwiththe'good_answers'param.
        (It'sassumedthatwronganswersareatindex0ofquestion.suggested_answer_idsandgoodanswersatindex1)"""
        answer.write({
            'state':'done',
            'user_input_line_ids':[
                (0,0,{
                    'question_id':question.id,
                    'answer_type':'suggestion',
                    'answer_score':1ifgood_answerselse0,
                    'suggested_answer_id':question.suggested_answer_ids[1ifgood_answerselse0].id
                })forquestioninquestions
            ]
        })
