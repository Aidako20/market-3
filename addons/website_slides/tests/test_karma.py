#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_slides.testsimportcommon
fromflectra.testsimporttagged
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger


@tagged('functional')
classTestKarmaGain(common.SlidesCase):

    defsetUp(self):
        super(TestKarmaGain,self).setUp()

        self.channel_2=self.env['slide.channel'].with_user(self.user_officer).create({
            'name':'TestChannel2',
            'channel_type':'training',
            'promote_strategy':'most_voted',
            'enroll':'public',
            'visibility':'public',
            'is_published':True,
            'karma_gen_channel_finish':100,
            'karma_gen_slide_vote':5,
            'karma_gen_channel_rank':10,
        })

        self.slide_2_0=self.env['slide.slide'].with_user(self.user_officer).create({
            'name':'Howtotravelthroughspaceandtime',
            'channel_id':self.channel_2.id,
            'slide_type':'presentation',
            'is_published':True,
            'completion_time':2.0,
        })
        self.slide_2_1=self.env['slide.slide'].with_user(self.user_officer).create({
            'name':'Howtoduplicateyourself',
            'channel_id':self.channel_2.id,
            'slide_type':'presentation',
            'is_published':True,
            'completion_time':2.0,
        })

    @mute_logger('flectra.models')
    @users('user_emp','user_portal','user_officer')
    deftest_karma_gain(self):
        user=self.env.user
        user.write({'karma':0})
        computed_karma=0

        #Addtheusertothecourse
        (self.channel|self.channel_2)._action_add_members(user.partner_id)
        self.assertEqual(user.karma,0)

        #FinishtheCourse
        self.slide.with_user(user).action_set_completed()
        self.assertFalse(self.channel.with_user(user).completed)
        self.slide_2.with_user(user).action_set_completed()

        #answeraquizzquestion
        self.slide_3.with_user(user).action_set_viewed(quiz_attempts_inc=True)
        self.slide_3.with_user(user)._action_set_quiz_done()
        self.slide_3.with_user(user).action_set_completed()
        computed_karma+=self.slide_3.quiz_first_attempt_reward
        computed_karma+=self.channel.karma_gen_channel_finish

        self.assertTrue(self.channel.with_user(user).completed)
        self.assertEqual(user.karma,computed_karma)

        #BeginthenfinishthesecondCourse
        self.slide_2_0.with_user(user).action_set_completed()
        self.assertFalse(self.channel_2.with_user(user).completed)
        self.assertEqual(user.karma,computed_karma)

        self.slide_2_1.with_user(user).action_set_completed()
        self.assertTrue(self.channel_2.with_user(user).completed)
        computed_karma+=self.channel_2.karma_gen_channel_finish
        self.assertEqual(user.karma,computed_karma)

        #Voteforaslide
        slide_user=self.slide.with_user(user)
        slide_user.action_like()
        computed_karma+=self.channel.karma_gen_slide_vote
        self.assertEqual(user.karma,computed_karma)
        slide_user.action_like() #re-likesomethingalreadylikedshouldnotaddkarmaagain
        self.assertEqual(user.karma,computed_karma)
        slide_user.action_dislike()
        computed_karma-=self.channel.karma_gen_slide_vote
        self.assertEqual(user.karma,computed_karma)
        slide_user.action_dislike()
        computed_karma-=self.channel.karma_gen_slide_vote
        self.assertEqual(user.karma,computed_karma)
        slide_user.action_dislike() #dislikeagainsomethingalreadydislikedshouldnotremovekarmaagain
        self.assertEqual(user.karma,computed_karma)

        #Leavethefinishedcourse
        self.channel._remove_membership(user.partner_id.ids)
        computed_karma-=self.channel.karma_gen_channel_finish
        computed_karma-=self.slide_3.quiz_first_attempt_reward
        self.assertEqual(user.karma,computed_karma)

    @mute_logger('flectra.models')
    @users('user_emp','user_portal','user_officer')
    deftest_karma_gain_multiple_course(self):
        user=self.env.user
        user.write({'karma':0})
        computed_karma=0

        #Finishtwocourseatthesametime(shouldnoteverhappenbuthey,weneverknow)
        (self.channel|self.channel_2)._action_add_members(user.partner_id)

        computed_karma+=self.channel.karma_gen_channel_finish+self.channel_2.karma_gen_channel_finish
        (self.slide|self.slide_2|self.slide_3|self.slide_2_0|self.slide_2_1).with_user(user).action_set_completed()
        self.assertEqual(user.karma,computed_karma)
