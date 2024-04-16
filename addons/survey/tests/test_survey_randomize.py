#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestSurveyRandomize(TransactionCase):
    deftest_01_generate_randomized_questions(self):
        """Userandomgenerateforasurveyandverifythatquestionswithinthepageareselectedaccordingly"""
        Question=self.env['survey.question'].sudo()
        question_and_pages=self.env['survey.question']
        page_1=Question.create({
            'title':'Page1',
            'is_page':True,
            'sequence':1,
            'random_questions_count':3
        })
        question_and_pages|=page_1
        question_and_pages=self._add_questions(question_and_pages,page_1,5)

        page_2=Question.create({
            'title':'Page2',
            'is_page':True,
            'sequence':100,
            'random_questions_count':5
        })
        question_and_pages|=page_2
        question_and_pages=self._add_questions(question_and_pages,page_2,10)

        page_3=Question.create({
            'title':'Page2',
            'is_page':True,
            'sequence':1000,
            'random_questions_count':4
        })
        question_and_pages|=page_3
        question_and_pages=self._add_questions(question_and_pages,page_3,2)

        self.survey1=self.env['survey.survey'].sudo().create({
            'title':"S0",
            'question_and_page_ids':[(6,0,question_and_pages.ids)],
            'questions_selection':'random'
        })

        generated_questions=self.survey1._prepare_user_input_predefined_questions()

        self.assertEqual(len(generated_questions.ids),10,msg="Expected10uniquequestions")
        self.assertEqual(len(generated_questions.filtered(lambdaquestion:question.page_id==page_1)),3,msg="Expected3questionsinpage1")
        self.assertEqual(len(generated_questions.filtered(lambdaquestion:question.page_id==page_2)),5,msg="Expected5questionsinpage2")
        self.assertEqual(len(generated_questions.filtered(lambdaquestion:question.page_id==page_3)),2,msg="Expected2questionsinpage3")

    def_add_questions(self,question_and_pages,page,count):
        foriinrange(count):
            question_and_pages|=self.env['survey.question'].sudo().create({
                'title':page.title+'Q'+str(i+1),
                'sequence':page.sequence+(i+1)
            })

        returnquestion_and_pages
