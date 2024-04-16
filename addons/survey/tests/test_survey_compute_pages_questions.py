#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.survey.testsimportcommon


classTestSurveyComputePagesQuestions(common.TestSurveyCommon):
    deftest_compute_pages_questions(self):
        withself.with_user('survey_manager'):
            survey=self.env['survey.survey'].create({
                'title':'Testcomputesurvey',
                'state':'open',
            })

            page_0=self.env['survey.question'].create({
                'is_page':True,
                'sequence':1,
                'title':'P1',
                'survey_id':survey.id
            })
            page0_q0=self._add_question(page_0,'Q1','text_box',survey_id=survey.id)
            page0_q1=self._add_question(page_0,'Q2','text_box',survey_id=survey.id)
            page0_q2=self._add_question(page_0,'Q3','text_box',survey_id=survey.id)
            page0_q3=self._add_question(page_0,'Q4','text_box',survey_id=survey.id)
            page0_q4=self._add_question(page_0,'Q5','text_box',survey_id=survey.id)

            page_1=self.env['survey.question'].create({
                'is_page':True,
                'sequence':7,
                'title':'P2',
                'survey_id':survey.id,
            })
            page1_q0=self._add_question(page_1,'Q6','text_box',survey_id=survey.id)
            page1_q1=self._add_question(page_1,'Q7','text_box',survey_id=survey.id)
            page1_q2=self._add_question(page_1,'Q8','text_box',survey_id=survey.id)
            page1_q3=self._add_question(page_1,'Q9','text_box',survey_id=survey.id)

        self.assertEqual(len(survey.page_ids),2,"Surveyshouldhave2pages")
        self.assertIn(page_0,survey.page_ids,"Page1shouldbecontainedinsurvey'spage_ids")
        self.assertIn(page_1,survey.page_ids,"Page2shouldbecontainedinsurvey'spage_ids")

        self.assertEqual(len(page_0.question_ids),5,"Page1shouldhave5questions")
        self.assertIn(page0_q0,page_0.question_ids,"Question1shouldbeinpage1")
        self.assertIn(page0_q1,page_0.question_ids,"Question2shouldbeinpage1")
        self.assertIn(page0_q2,page_0.question_ids,"Question3shouldbeinpage1")
        self.assertIn(page0_q3,page_0.question_ids,"Question4shouldbeinpage1")
        self.assertIn(page0_q4,page_0.question_ids,"Question5shouldbeinpage1")

        self.assertEqual(len(page_1.question_ids),4,"Page2shouldhave4questions")
        self.assertIn(page1_q0,page_1.question_ids,"Question6shouldbeinpage2")
        self.assertIn(page1_q1,page_1.question_ids,"Question7shouldbeinpage2")
        self.assertIn(page1_q2,page_1.question_ids,"Question8shouldbeinpage2")
        self.assertIn(page1_q3,page_1.question_ids,"Question9shouldbeinpage2")

        self.assertEqual(page0_q0.page_id,page_0,"Question1shouldbelongtopage1")
        self.assertEqual(page0_q1.page_id,page_0,"Question2shouldbelongtopage1")
        self.assertEqual(page0_q2.page_id,page_0,"Question3shouldbelongtopage1")
        self.assertEqual(page0_q3.page_id,page_0,"Question4shouldbelongtopage1")
        self.assertEqual(page0_q4.page_id,page_0,"Question5shouldbelongtopage1")

        self.assertEqual(page1_q0.page_id,page_1,"Question6shouldbelongtopage2")
        self.assertEqual(page1_q1.page_id,page_1,"Question7shouldbelongtopage2")
        self.assertEqual(page1_q2.page_id,page_1,"Question8shouldbelongtopage2")
        self.assertEqual(page1_q3.page_id,page_1,"Question9shouldbelongtopage2")

        #move1questionfrompage1topage2
        page0_q2.write({'sequence':12})
        page0_q2._compute_page_id()
        self.assertEqual(page0_q2.page_id,page_1,"Question3shouldnowbelongtopage2")
