#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields
fromflectra.tests.commonimporttagged,HttpCase


@tagged('post_install','-at_install')
classTestUiSession(HttpCase):
    deftest_admin_survey_session(self):
        """Thismethodtestsafull'surveysession'flow.
        Breakdownofdifferentsteps:
        -Createthetestdata
          -Ascoredsurvey
          -Anicknamequestion
          -"Simple"typequestions(text,date,datetime)
          -Aregularsimplechoice
          -Ascoredsimplechoice
          -AscoredANDtimedmultiplechoice
        -Createanewsurveysession
        -Register3attendeestoit
        -Openthesessionmanagertocheckthatourattendeesareaccountedfor
        -Createsomeanswerstooursurveyquestions.
        -Thenrunthe'big'managesessiontour(seeJSdocfordetails)
        -Andfinallycheckthatoursessionandattendeesinputsarecorrectlyclosed."""

        #=======================
        #CREATESURVEYTESTDATA
        #=======================

        test_start_time=fields.Datetime.now()

        survey_session=self.env['survey.survey'].create({
            'title':'UserSessionSurvey',
            'access_token':'b137640d-14d4-4748-9ef6-344caaaaafe',
            'state':'open',
            'access_mode':'public',
            'users_can_go_back':False,
            'questions_layout':'page_per_question',
            'scoring_type':'scoring_without_answers'
        })

        nickname_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'Nickname',
            'save_as_nickname':True,
            'sequence':1,
            'question_type':'char_box',
        })
        text_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'TextQuestion',
            'sequence':2,
            'question_type':'char_box',
        })
        date_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'DateQuestion',
            'sequence':3,
            'question_type':'date',
        })
        datetime_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'DatetimeQuestion',
            'sequence':4,
            'question_type':'datetime',
        })
        simple_choice_answer_1=self.env['survey.question.answer'].create({
            'value':'First'
        })
        simple_choice_answer_2=self.env['survey.question.answer'].create({
            'value':'Second'
        })
        simple_choice_answer_3=self.env['survey.question.answer'].create({
            'value':'Third'
        })
        simple_choice_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'RegularSimpleChoice',
            'sequence':5,
            'question_type':'simple_choice',
            'suggested_answer_ids':[
                (4,simple_choice_answer_1.id),
                (4,simple_choice_answer_2.id),
                (4,simple_choice_answer_3.id)],
        })
        scored_choice_answer_1=self.env['survey.question.answer'].create({
            'value':'Correct',
            'is_correct':True,
            'answer_score':30
        })
        scored_choice_answer_2=self.env['survey.question.answer'].create({
            'value':'Incorrect1'
        })
        scored_choice_answer_3=self.env['survey.question.answer'].create({
            'value':'Incorrect2'
        })
        scored_choice_answer_4=self.env['survey.question.answer'].create({
            'value':'Incorrect3'
        })
        scored_choice_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'ScoredSimpleChoice',
            'sequence':6,
            'question_type':'simple_choice',
            'suggested_answer_ids':[
                (4,scored_choice_answer_1.id),
                (4,scored_choice_answer_2.id),
                (4,scored_choice_answer_3.id),
                (4,scored_choice_answer_4.id)],
        })
        timed_scored_choice_answer_1=self.env['survey.question.answer'].create({
            'value':'Correct',
            'is_correct':True,
            'answer_score':30
        })
        timed_scored_choice_answer_2=self.env['survey.question.answer'].create({
            'value':'Alsocorrectbutlesspoints',
            'is_correct':True,
            'answer_score':10
        })
        timed_scored_choice_answer_3=self.env['survey.question.answer'].create({
            'value':'Incorrect',
            'answer_score':-40
        })
        timed_scored_choice_question=self.env['survey.question'].create({
            'survey_id':survey_session.id,
            'title':'TimedScoredMultipleChoice',
            'sequence':6,
            'question_type':'multiple_choice',
            'is_time_limited':True,
            'time_limit':1,
            'suggested_answer_ids':[
                (4,timed_scored_choice_answer_1.id),
                (4,timed_scored_choice_answer_2.id),
                (4,timed_scored_choice_answer_3.id)],
        })

        #=======================
        #PART1:CREATESESSION
        #=======================

        self.start_tour('/web','test_survey_session_create_tour',login='admin')

        #trickypart:weonlytakeintoaccountanswerscreatedafterthesession_start_time
        #thecreate_dateoftheanswerswejustsavedissettothebeginningofthetest.
        #butthesession_start_timeissetafterthat.
        #Sowecheatonthesessionstartdatetobeabletocountanswersproperly.
        survey_session.write({'session_start_time':test_start_time-relativedelta(minutes=10)})

        attendee_1=survey_session._create_answer()
        attendee_2=survey_session._create_answer()
        attendee_3=survey_session._create_answer()
        all_attendees=[attendee_1,attendee_2,attendee_3]

        self.assertEqual('ready',survey_session.session_state)
        self.assertTrue(all(attendee.is_session_answerforattendeeinall_attendees),
            "Createdanswersshouldbewithinthesession.")
        self.assertTrue(all(attendee.state=='new'forattendeeinall_attendees),
            "Createdanswersshouldbeinthe'new'state.")

        #=========================================
        #PART2:OPENSESSIONANDCHECKATTENDEES
        #=========================================

        self.start_tour('/web','test_survey_session_start_tour',login='admin')

        self.assertEqual('in_progress',survey_session.session_state)
        self.assertTrue(bool(survey_session.session_start_time))

        #========================================
        #PART3:CREATEANSWERS&MANAGESESSION
        #========================================

        #createafewanswersbeforehandtoavoidhavingtobackandforthtoo
        #manytimesbetweenthetoursandthepythontest

        attendee_1.save_lines(nickname_question,'xxxTheBestxxx')
        attendee_2.save_lines(nickname_question,'azerty')
        attendee_3.save_lines(nickname_question,'nicktalope')
        self.assertEqual('xxxTheBestxxx',attendee_1.nickname)
        self.assertEqual('azerty',attendee_2.nickname)
        self.assertEqual('nicktalope',attendee_3.nickname)

        attendee_1.save_lines(text_question,'Attendee1isthebest')
        attendee_2.save_lines(text_question,'Attendee2rulez')
        attendee_3.save_lines(text_question,'Attendee3willcrushyou')
        attendee_1.save_lines(date_question,'2010-10-10')
        attendee_2.save_lines(date_question,'2011-11-11')
        attendee_2.save_lines(datetime_question,'2010-10-1010:00:00')
        attendee_3.save_lines(datetime_question,'2011-11-1115:55:55')
        attendee_1.save_lines(simple_choice_question,simple_choice_answer_1.id)
        attendee_2.save_lines(simple_choice_question,simple_choice_answer_1.id)
        attendee_3.save_lines(simple_choice_question,simple_choice_answer_2.id)
        attendee_1.save_lines(scored_choice_question,scored_choice_answer_1.id)
        attendee_2.save_lines(scored_choice_question,scored_choice_answer_2.id)
        attendee_3.save_lines(scored_choice_question,scored_choice_answer_3.id)
        attendee_1.save_lines(timed_scored_choice_question,
            [timed_scored_choice_answer_1.id,timed_scored_choice_answer_3.id])
        attendee_2.save_lines(timed_scored_choice_question,
            [timed_scored_choice_answer_1.id,timed_scored_choice_answer_2.id])
        attendee_3.save_lines(timed_scored_choice_question,
            [timed_scored_choice_answer_2.id])

        self.start_tour('/web','test_survey_session_manage_tour',login='admin')

        self.assertFalse(bool(survey_session.session_state))
        self.assertTrue(all(answer.state=='done'foranswerinall_attendees))
