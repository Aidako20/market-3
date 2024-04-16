#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.survey.testsimportcommon
frompsycopg2importIntegrityError
fromflectra.exceptionsimportAccessError
fromflectra.toolsimportmute_logger


classTestCertificationBadge(common.TestSurveyCommon):

    defsetUp(self):
        super(TestCertificationBadge,self).setUp()
        self.certification_survey=self.env['survey.survey'].with_user(self.survey_manager).create({
            'title':'CertificationSurvey',
            'access_mode':'public',
            'users_login_required':True,
            'scoring_type':'scoring_with_answers',
            'certification':True,
            'state':'open',
        })

        self.certification_survey_2=self.env['survey.survey'].with_user(self.survey_manager).create({
            'title':'AnotherCertificationSurvey',
            'access_mode':'public',
            'users_login_required':True,
            'scoring_type':'scoring_with_answers',
            'certification':True,
            'state':'open',
        })

        self.certification_badge=self.env['gamification.badge'].with_user(self.survey_manager).create({
            'name':self.certification_survey.title,
            'description':'Congratulations,youhavesucceededthiscertification',
            'rule_auth':'nobody',
            'level':None,
        })

        self.certification_badge_2=self.env['gamification.badge'].with_user(self.survey_manager).create({
            'name':self.certification_survey.title+'2',
            'description':'Congratulations,youhavesucceededthiscertification',
            'rule_auth':'nobody',
            'level':None,
        })

        self.certification_badge_3=self.env['gamification.badge'].with_user(self.survey_manager).create({
            'name':self.certification_survey.title+'3',
            'description':'Congratulations,youhavesucceededthiscertification',
            'rule_auth':'nobody',
            'level':None,
        })

    deftest_archive(self):
        """Archivestatusofsurveyispropagatedtoitsbadges."""
        self.certification_survey.write({
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge.id
        })

        self.certification_survey.action_archive()
        self.assertFalse(self.certification_survey.active)
        self.assertFalse(self.certification_badge.active)

        self.certification_survey.action_unarchive()
        self.assertTrue(self.certification_survey.active)
        self.assertTrue(self.certification_badge.active)

    deftest_give_badge_without_badge(self):
        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError):
                self.certification_survey.write({'certification_give_badge':True})
                self.certification_survey.flush(['certification_give_badge'])

    deftest_remove_badge_with_give_badge(self):
        self.certification_survey.write({
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge.id
        })
        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError):
                self.certification_survey.write({'certification_badge_id':None})
                self.certification_survey.flush(['certification_badge_id'])

    deftest_remove_badge_with_give_badge_multi(self):
        self.certification_survey.write({
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge.id
        })
        self.certification_survey_2.write({
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge_2.id
        })
        surveys=self.env['survey.survey'].browse([
            self.certification_survey.id,
            self.certification_survey_2.id
        ])
        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError):
                surveys.write({'certification_badge_id':None})
                surveys.flush(['certification_badge_id'])

    deftest_set_same_badge_on_multiple_survey(self):
        self.certification_survey.write({
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge.id
        })
        #setthesamebadgeonanothersurveyshouldfail:
        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError):
                self.certification_survey_2.write({
                    'certification_give_badge':True,
                    'certification_badge_id':self.certification_badge.id
                })
                self.certification_survey.flush()

    deftest_badge_configuration(self):
        #addacertificationbadgeonanewsurvey
        challenge=self.env['gamification.challenge'].search([('reward_id','=',self.certification_badge.id)])
        self.assertEqual(len(challenge),0,"""Achallengeshouldnotexistorbelinkedtothecertificationbadge
            ifthecertificationbadgehavenotbeenactivatedonacertificationsurvey""")

        self.certification_survey.write({
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge.id
        })

        challenge=self.env['gamification.challenge'].search([('reward_id','=',self.certification_badge.id)])
        self.assertEqual(len(challenge),1,
            "Achallengeshouldbecreatedifthecertificationbadgeisactivatedonacertificationsurvey")
        challenge_line=self.env['gamification.challenge.line'].search([('challenge_id','=',challenge.id)])
        self.assertEqual(len(challenge_line),1,
            "Achallenge_lineshouldbecreatedifthecertificationbadgeisactivatedonacertificationsurvey")
        goal=challenge_line.definition_id
        self.assertEqual(len(goal),1,
            "Agoalshouldbecreatedifthecertificationbadgeisactivatedonacertificationsurvey")

        #don'tgivebadgeanymore
        self.certification_survey.write({'certification_give_badge':False})
        self.assertEqual(self.certification_badge.id,self.certification_survey.certification_badge_id.id,
                         'Thecertificationbadgeshouldstillbesetoncertificationsurveyevenifgive_badgeisfalse.')
        self.assertEqual(self.certification_badge.active,False,
                         'Thecertificationbadgeshouldbeinactiveifgive_badgeisfalse.')

        challenge=self.env['gamification.challenge'].search([('id','=',challenge.id)])
        self.assertEqual(len(challenge),0,
            "Thechallengeshouldbedeletedifthecertificationbadgeisunsetfromthecertificationsurvey")
        challenge_line=self.env['gamification.challenge.line'].search([('id','=',challenge_line.id)])
        self.assertEqual(len(challenge_line),0,
            "Thechallenge_lineshouldbedeletedifthecertificationbadgeisunsetfromthecertificationsurvey")
        goal=self.env['gamification.goal'].search([('id','=',goal.id)])
        self.assertEqual(len(goal),0,
            "Thegoalshouldbedeletedifthecertificationbadgeisunsetfromthecertificationsurvey")

        #reactivethebadgeinthesurvey
        self.certification_survey.write({'certification_give_badge':True})
        self.assertEqual(self.certification_badge.active,True,
                         'Thecertificationbadgeshouldbeactiveifgive_badgeistrue.')

        challenge=self.env['gamification.challenge'].search([('reward_id','=',self.certification_badge.id)])
        self.assertEqual(len(challenge),1,
            "Achallengeshouldbecreatedifthecertificationbadgeisactivatedonacertificationsurvey")
        challenge_line=self.env['gamification.challenge.line'].search([('challenge_id','=',challenge.id)])
        self.assertEqual(len(challenge_line),1,
            "Achallenge_lineshouldbecreatedifthecertificationbadgeisactivatedonacertificationsurvey")
        goal=challenge_line.definition_id
        self.assertEqual(len(goal),1,
            "Agoalshouldbecreatedifthecertificationbadgeisactivatedonacertificationsurvey")

    deftest_certification_badge_access(self):
        self.certification_badge.with_user(self.survey_manager).write(
            {'description':"Spoileralert:I'mAegonTargaryenandIsleepwiththeDragonQueen,whoismyauntbytheway!SoIcandowhateverIwant!EvenifIknownothing!"})
        self.certification_badge.with_user(self.survey_user).write({'description':"YoupieYeay!"})
        withself.assertRaises(AccessError):
            self.certification_badge.with_user(self.user_emp).write({'description':"I'madudewhothinkthathaseveryrightontheIronThrone"})
        withself.assertRaises(AccessError):
            self.certification_badge.with_user(self.user_portal).write({'description':"Guy,youjustcan'tdothat!"})
        withself.assertRaises(AccessError):
            self.certification_badge.with_user(self.user_public).write({'description':"Whatdidyouexpect?Schwepps!"})

    deftest_badge_configuration_multi(self):
        vals={
            'title':'CertificationSurvey',
            'access_mode':'public',
            'users_login_required':True,
            'scoring_type':'scoring_with_answers',
            'certification':True,
            'certification_give_badge':True,
            'certification_badge_id':self.certification_badge.id,
            'state':'open'
        }
        survey_1=self.env['survey.survey'].create(vals.copy())
        vals.update({'certification_badge_id':self.certification_badge_2.id})
        survey_2=self.env['survey.survey'].create(vals.copy())
        vals.update({'certification_badge_id':self.certification_badge_3.id})
        survey_3=self.env['survey.survey'].create(vals)

        certification_surveys=self.env['survey.survey'].browse([survey_1.id,survey_2.id,survey_3.id])
        self.assertEqual(len(certification_surveys),3,'Thereshouldbe3certificationsurveycreated')

        challenges=self.env['gamification.challenge'].search([('reward_id','in',certification_surveys.mapped('certification_badge_id').ids)])
        self.assertEqual(len(challenges),3,"3challengesshouldbecreated")
        challenge_lines=self.env['gamification.challenge.line'].search([('challenge_id','in',challenges.ids)])
        self.assertEqual(len(challenge_lines),3,"3challenge_linesshouldbecreated")
        goals=challenge_lines.mapped('definition_id')
        self.assertEqual(len(goals),3,"3goalsshouldbecreated")

        #Testwritemulti
        certification_surveys.write({'certification_give_badge':False})
        forsurveyincertification_surveys:
            self.assertEqual(survey.certification_badge_id.active,False,
                             'Everybadgeshouldbeinactiveifthe3surveydoesnotgivebadgeanymore')

        challenges=self.env['gamification.challenge'].search([('id','in',challenges.ids)])
        self.assertEqual(len(challenges),0,"The3challengesshouldbedeleted")
        challenge_lines=self.env['gamification.challenge.line'].search([('id','in',challenge_lines.ids)])
        self.assertEqual(len(challenge_lines),0,"The3challenge_linesshouldbedeleted")
        goals=self.env['gamification.goal'].search([('id','in',goals.ids)])
        self.assertEqual(len(goals),0,"The3goalsshouldbedeleted")

        certification_surveys.write({'certification_give_badge':True})
        forsurveyincertification_surveys:
            self.assertEqual(survey.certification_badge_id.active,True,
                             'Everybadgeshouldbereactivatedifthe3surveygivebadgesagain')

        challenges=self.env['gamification.challenge'].search([('reward_id','in',certification_surveys.mapped('certification_badge_id').ids)])
        self.assertEqual(len(challenges),3,"3challengesshouldbecreated")
        challenge_lines=self.env['gamification.challenge.line'].search([('challenge_id','in',challenges.ids)])
        self.assertEqual(len(challenge_lines),3,"3challenge_linesshouldbecreated")
        goals=challenge_lines.mapped('definition_id')
        self.assertEqual(len(goals),3,"3goalsshouldbecreated")
