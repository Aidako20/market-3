#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

from.commonimportKARMA,TestForumCommon
fromflectra.exceptionsimportUserError,AccessError
fromflectra.toolsimportmute_logger
frompsycopg2importIntegrityError


classTestForum(TestForumCommon):

    deftest_crud_rights(self):
        Post=self.env['forum.post']
        Vote=self.env['forum.post.vote']
        self.user_portal.karma=500
        self.user_employee.karma=500

        #createsomeposts
        self.admin_post=self.post
        self.portal_post=Post.with_user(self.user_portal).create({
            'name':'PostfromPortalUser',
            'content':'Iamnotabird.',
            'forum_id':self.forum.id,
        })
        self.employee_post=Post.with_user(self.user_employee).create({
            'name':'PostfromEmployeeUser',
            'content':'Iamnotabird.',
            'forum_id':self.forum.id,
        })

        #voteonsomeposts
        self.employee_vote_on_admin_post=Vote.with_user(self.user_employee).create({
            'post_id':self.admin_post.id,
            'vote':'1',
        })
        self.portal_vote_on_admin_post=Vote.with_user(self.user_portal).create({
            'post_id':self.admin_post.id,
            'vote':'1',
        })
        self.admin_vote_on_portal_post=Vote.create({
            'post_id':self.portal_post.id,
            'vote':'1',
        })
        self.admin_vote_on_employee_post=Vote.create({
            'post_id':self.employee_post.id,
            'vote':'1',
        })

        #Oneshouldnotbeabletomodifysomeoneelse'svote
        withself.assertRaises(UserError):
            self.admin_vote_on_portal_post.with_user(self.user_employee).write({
                'vote':'-1',
            })
        withself.assertRaises(UserError):
            self.admin_vote_on_employee_post.with_user(self.user_portal).write({
                'vote':'-1',
            })

        #Oneshouldnotbeabletogivehisvotetosomeoneelse
        self.employee_vote_on_admin_post.with_user(self.user_employee).write({
            'user_id':1,
        })
        self.assertEqual(self.employee_vote_on_admin_post.user_id,self.user_employee,'Useremployeeshouldnotbeabletogiveitsvoteownershiptosomeoneelse')
        #Oneshouldnotbeabletochangehisvote'sposttoapostofhisown(wouldbeselfvoting)
        withself.assertRaises(UserError):
            self.employee_vote_on_admin_post.with_user(self.user_employee).write({
                'post_id':self.employee_post.id,
            })

        #Oneshouldnotbeabletogivehisvotetosomeoneelse
        self.portal_vote_on_admin_post.with_user(self.user_portal).write({
            'user_id':1,
        })
        self.assertEqual(self.portal_vote_on_admin_post.user_id,self.user_portal,'Userportalshouldnotbeabletogiveitsvoteownershiptosomeoneelse')
        #Oneshouldnotbeabletochangehisvote'sposttoapostofhisown(wouldbeselfvoting)
        withself.assertRaises(UserError):
            self.portal_vote_on_admin_post.with_user(self.user_portal).write({
                'post_id':self.portal_post.id,
            })

        #Oneshouldnotbeabletovoteforitsownpost
        withself.assertRaises(UserError):
            Vote.with_user(self.user_employee).create({
                'post_id':self.employee_post.id,
                'vote':'1',
            })
        #Oneshouldnotbeabletovoteforitsownpost
        withself.assertRaises(UserError):
            Vote.with_user(self.user_portal).create({
                'post_id':self.portal_post.id,
                'vote':'1',
            })

        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError):
                withself.cr.savepoint():
                    #Oneshouldnotbeabletovotemorethanonceonasamepost
                    Vote.with_user(self.user_employee).create({
                        'post_id':self.admin_post.id,
                        'vote':'1',
                    })
            withself.assertRaises(IntegrityError):
                withself.cr.savepoint():
                    #Oneshouldnotbeabletovotemorethanonceonasamepost
                    Vote.with_user(self.user_employee).create({
                        'post_id':self.admin_post.id,
                        'vote':'1',
                    })

        #Oneshouldnotbeabletocreateavoteforsomeoneelse
        new_employee_vote=Vote.with_user(self.user_employee).create({
            'post_id':self.portal_post.id,
            'user_id':1,
            'vote':'1',
        })
        self.assertEqual(new_employee_vote.user_id,self.user_employee,'Creatingavoteforsomeoneelseshouldnotbeallowed.Itshouldcreateitforyourselfinstead')
        #Oneshouldnotbeabletocreateavoteforsomeoneelse
        new_portal_vote=Vote.with_user(self.user_portal).create({
            'post_id':self.employee_post.id,
            'user_id':1,
            'vote':'1',
        })
        self.assertEqual(new_portal_vote.user_id,self.user_portal,'Creatingavoteforsomeoneelseshouldnotbeallowed.Itshouldcreateitforyourselfinstead')

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_ask(self):
        Post=self.env['forum.post']

        #Publicuserasksaquestion:notallowed
        withself.assertRaises(AccessError):
            Post.with_user(self.user_public).create({
                'name':"Question?",
                'forum_id':self.forum.id,
            })

        #Portaluserasksaquestionwithtags:notallowed,unsufficientkarma
        withself.assertRaises(AccessError):
            Post.with_user(self.user_portal).create({
                'name':"Q_0",
                'forum_id':self.forum.id,
                'tag_ids':[(0,0,{'name':'Tag0','forum_id':self.forum.id})]
            })

        #Portaluserasksaquestionwithtags:okifenoughkarma
        self.user_portal.karma=KARMA['tag_create']
        Post.with_user(self.user_portal).create({
            'name':"Q0",
            'forum_id':self.forum.id,
            'tag_ids':[(0,0,{'name':'Tag1','forum_id':self.forum.id})]
        })
        self.assertEqual(self.user_portal.karma,KARMA['tag_create'],'website_forum:wrongkarmagenerationwhenaskingquestion')

        self.user_portal.karma=KARMA['post']
        Post.with_user(self.user_portal).create({
            'name':"Q0",
            'forum_id':self.forum.id,
            'tag_ids':[(0,0,{'name':'Tag42','forum_id':self.forum.id})]
        })
        self.assertEqual(self.user_portal.karma,KARMA['post']+KARMA['gen_que_new'],'website_forum:wrongkarmagenerationwhenaskingquestion')

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_answer(self):
        Post=self.env['forum.post']

        #Answersitsownquestion:notallowed,unsufficientkarma
        withself.assertRaises(AccessError):
            Post.with_user(self.user_employee).create({
                'name':"A0",
                'forum_id':self.forum.id,
                'parent_id':self.post.id,
            })

        #Answersonquestion:okifenoughkarma
        self.user_employee.karma=KARMA['ans']
        Post.with_user(self.user_employee).create({
            'name':"A0",
            'forum_id':self.forum.id,
            'parent_id':self.post.id,
        })
        self.assertEqual(self.user_employee.karma,KARMA['ans'],'website_forum:wrongkarmagenerationwhenansweringquestion')

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_vote_crash(self):
        Post=self.env['forum.post']
        self.user_employee.karma=KARMA['ans']
        emp_answer=Post.with_user(self.user_employee).create({
            'name':'TestAnswer',
            'forum_id':self.forum.id,
            'parent_id':self.post.id})

        #upvoteitsownpost
        withself.assertRaises(UserError):
            emp_answer.vote(upvote=True)

        #notenoughkarma
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).vote(upvote=True)

    deftest_vote(self):
        defcheck_vote_records_count_and_integrity(expected_total_votes_count):
            groups=self.env['forum.post.vote'].read_group([],fields=['__count'],groupby=['post_id','user_id'],lazy=False)
            self.assertEqual(len(groups),expected_total_votes_count)
            forpost_user_groupingroups:
                self.assertEqual(post_user_group['__count'],1)

        check_vote_records_count_and_integrity(2)
        self.post.create_uid.karma=KARMA['ask']
        self.user_portal.karma=KARMA['dwv']
        initial_vote_count=self.post.vote_count
        post_as_portal=self.post.with_user(self.user_portal)
        res=post_as_portal.vote(upvote=True)

        self.assertEqual(res['user_vote'],'1')
        self.assertEqual(res['vote_count'],initial_vote_count+1)
        self.assertEqual(post_as_portal.user_vote,1)
        self.assertEqual(self.post.create_uid.karma,KARMA['ask']+KARMA['gen_que_upv'],'website_forum:wrongkarmagenerationofupvotedquestionauthor')

        #Onvotingagainwiththesamevalue,nothingchanges
        res=post_as_portal.vote(upvote=True)
        self.assertEqual(res['vote_count'],initial_vote_count+1)
        self.assertEqual(res['user_vote'],'1')
        self.post.invalidate_cache()
        self.assertEqual(post_as_portal.user_vote,1)

        #Onrevertingvote,votecancels
        res=post_as_portal.vote(upvote=False)
        self.assertEqual(res['vote_count'],initial_vote_count)
        self.assertEqual(res['user_vote'],'0')
        self.post.invalidate_cache()
        self.assertEqual(post_as_portal.user_vote,0)

        #Everythingworksfrom"0"too
        res=post_as_portal.vote(upvote=False)
        self.assertEqual(res['vote_count'],initial_vote_count-1)
        self.assertEqual(res['user_vote'],'-1')
        self.post.invalidate_cache()
        self.assertEqual(post_as_portal.user_vote,-1)

        check_vote_records_count_and_integrity(3)

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_downvote_crash(self):
        Post=self.env['forum.post']
        self.user_employee.karma=KARMA['ans']
        emp_answer=Post.with_user(self.user_employee).create({
            'name':'TestAnswer',
            'forum_id':self.forum.id,
            'parent_id':self.post.id})

        #downvoteitsownpost
        withself.assertRaises(UserError):
            emp_answer.vote(upvote=False)

        #notenoughkarma
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).vote(upvote=False)

    deftest_downvote(self):
        self.post.create_uid.karma=50
        self.user_portal.karma=KARMA['dwv']
        self.post.with_user(self.user_portal).vote(upvote=False)
        self.assertEqual(self.post.create_uid.karma,50+KARMA['gen_que_dwv'],'website_forum:wrongkarmagenerationofdownvotedquestionauthor')

    deftest_comment_crash(self):
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).message_post(body='Shouldcrash',message_type='comment')

    deftest_comment(self):
        self.post.with_user(self.user_employee).message_post(body='Test0',message_type='notification')
        self.user_employee.karma=KARMA['com_all']
        self.post.with_user(self.user_employee).message_post(body='Test1',message_type='comment')
        self.assertEqual(len(self.post.message_ids),4,'website_forum:wrongbehaviorofmessage_post')

    deftest_flag_a_post(self):
        Post=self.env['forum.post']
        self.user_portal.karma=KARMA['ask']
        post=Post.with_user(self.user_portal).create({
            'name':"Q0",
            'forum_id':self.forum.id,
        })

        #portaluserflagsapost:notallowed,unsufficientkarma
        withself.assertRaises(AccessError):
            post.with_user(self.user_portal).flag()

        #portaluserflagsapost:okifenoughkarma
        self.user_portal.karma=KARMA['flag']
        post.state='active'
        post.with_user(self.user_portal).flag()
        self.assertEqual(post.state,'flagged','website_forum:wrongstatewhenflaggingapost')

    deftest_validate_a_post(self):
        Post=self.env['forum.post']
        self.user_portal.karma=KARMA['ask']
        post=Post.with_user(self.user_portal).create({
            'name':"Q0",
            'forum_id':self.forum.id,
        })

        #portaluservalidateapost:notallowed,unsufficientkarma
        withself.assertRaises(AccessError):
            post.with_user(self.user_portal).validate()

        #portaluservalidateapendingpost
        self.user_portal.karma=KARMA['moderate']
        post.state='pending'
        init_karma=post.create_uid.karma
        post.with_user(self.user_portal).validate()
        self.assertEqual(post.state,'active','website_forum:wrongstatewhenvalidateapostafterpending')
        self.assertEqual(post.create_uid.karma,init_karma+KARMA['gen_que_new'],'website_forum:wrongkarmawhenvalidateapostafterpending')

        #portaluservalidateaflaggedpost:okifenoughkarma
        self.user_portal.karma=KARMA['moderate']
        post.state='flagged'
        post.with_user(self.user_portal).validate()
        self.assertEqual(post.state,'active','website_forum:wrongstatewhenvalidateapostafterflagged')

        #portaluservalidateanoffensivepost:okifenoughkarma
        self.user_portal.karma=KARMA['moderate']
        post.state='offensive'
        init_karma=post.create_uid.karma
        post.with_user(self.user_portal).validate()
        self.assertEqual(post.state,'active','website_forum:wrongstatewhenvalidateapostafteroffensive')

    deftest_refuse_a_post(self):
        Post=self.env['forum.post']
        self.user_portal.karma=KARMA['ask']
        post=Post.with_user(self.user_portal).create({
            'name':"Q0",
            'forum_id':self.forum.id,
        })

        #portaluservalidateapost:notallowed,unsufficientkarma
        withself.assertRaises(AccessError):
            post.with_user(self.user_portal).refuse()

        #portaluservalidateapendingpost
        self.user_portal.karma=KARMA['moderate']
        post.state='pending'
        init_karma=post.create_uid.karma
        post.with_user(self.user_portal).refuse()
        self.assertEqual(post.moderator_id,self.user_portal,'website_forum:wrongmoderator_idwhenrefusing')
        self.assertEqual(post.create_uid.karma,init_karma,'website_forum:wrongkarmawhenrefusingapost')

    deftest_mark_a_post_as_offensive(self):
        Post=self.env['forum.post']
        self.user_portal.karma=KARMA['ask']
        post=Post.with_user(self.user_portal).create({
            'name':"Q0",
            'forum_id':self.forum.id,
        })

        #portalusermarkapostasoffensive:notallowed,unsufficientkarma
        withself.assertRaises(AccessError):
            post.with_user(self.user_portal).mark_as_offensive(12)

        #portalusermarkapostasoffensive
        self.user_portal.karma=KARMA['moderate']
        post.state='flagged'
        init_karma=post.create_uid.karma
        post.with_user(self.user_portal).mark_as_offensive(12)
        self.assertEqual(post.state,'offensive','website_forum:wrongstatewhenmarkingapostasoffensive')
        self.assertEqual(post.create_uid.karma,init_karma+KARMA['gen_ans_flag'],'website_forum:wrongkarmawhenmarkingapostasoffensive')

    deftest_convert_answer_to_comment_crash(self):
        Post=self.env['forum.post']

        #convertingaquestiondoesnothing
        new_msg=self.post.with_user(self.user_portal).convert_answer_to_comment()
        self.assertEqual(new_msg.id,False,'website_forum:questiontocommentconversionfailed')
        self.assertEqual(Post.search([('name','=','TestQuestion')])[0].forum_id.name,'TestForum','website_forum:questiontocommentconversionfailed')

        withself.assertRaises(AccessError):
            self.answer.with_user(self.user_portal).convert_answer_to_comment()

    deftest_convert_answer_to_comment(self):
        self.user_portal.karma=KARMA['com_conv_all']
        post_author=self.answer.create_uid.partner_id
        new_msg=self.answer.with_user(self.user_portal).convert_answer_to_comment()
        self.assertEqual(len(new_msg),1,'website_forum:wronganswertocommentconversion')
        self.assertEqual(new_msg.author_id,post_author,'website_forum:wronganswertocommentconversion')
        self.assertIn('Iamananteater',new_msg.body,'website_forum:wronganswertocommentconversion')

    deftest_edit_post_crash(self):
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).write({'name':'Iamnotyourfather.'})

    deftest_edit_post(self):
        self.post.create_uid.karma=KARMA['edit_own']
        self.post.write({'name':'ActuallyIamyourdog.'})
        self.user_portal.karma=KARMA['edit_all']
        self.post.with_user(self.user_portal).write({'name':'ActuallyIamyourcat.'})

    deftest_close_post_crash(self):
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).close(None)

    deftest_close_post_own(self):
        self.post.create_uid.karma=KARMA['close_own']
        self.post.close(None)

    deftest_close_post_all(self):
        self.user_portal.karma=KARMA['close_all']
        self.post.with_user(self.user_portal).close(None)

    deftest_deactivate_post_crash(self):
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).write({'active':False})

    deftest_deactivate_post_own(self):
        self.post.create_uid.karma=KARMA['unlink_own']
        self.post.write({'active':False})

    deftest_deactivate_post_all(self):
        self.user_portal.karma=KARMA['unlink_all']
        self.post.with_user(self.user_portal).write({'active':False})

    deftest_unlink_post_crash(self):
        withself.assertRaises(AccessError):
            self.post.with_user(self.user_portal).unlink()

    deftest_unlink_post_own(self):
        self.post.create_uid.karma=KARMA['unlink_own']
        self.post.unlink()

    deftest_unlink_post_all(self):
        self.user_portal.karma=KARMA['unlink_all']
        self.post.with_user(self.user_portal).unlink()

    deftest_forum_mode_questions(self):
        Forum=self.env['forum.forum']
        forum_questions=Forum.create({
            'name':'QuestionsForum',
            'mode':'questions',
            'active':True
        })
        Post=self.env['forum.post']
        questions_post=Post.create({
            'name':'MyFirstPost',
            'forum_id':forum_questions.id,
            'parent_id':self.post.id,
        })
        answer_to_questions_post=Post.create({
            'name':'Thisisananswer',
            'forum_id':forum_questions.id,
            'parent_id':questions_post.id,
        })
        self.assertEqual(
            notquestions_post.uid_has_answeredorquestions_post.forum_id.mode=='discussions',False)
        self.assertEqual(
            questions_post.uid_has_answeredandquestions_post.forum_id.mode=='questions',True)

    deftest_forum_mode_discussions(self):
        Forum=self.env['forum.forum']
        forum_discussions=Forum.create({
            'name':'DiscussionsForum',
            'mode':'discussions',
            'active':True
        })
        Post=self.env['forum.post']
        discussions_post=Post.create({
            'name':'MyFirstPost',
            'forum_id':forum_discussions.id,
            'parent_id':self.post.id,
        })
        answer_to_discussions_post=Post.create({
            'name':'Thisisananswer',
            'forum_id':forum_discussions.id,
            'parent_id':discussions_post.id,
        })
        self.assertEqual(
            notdiscussions_post.uid_has_answeredordiscussions_post.forum_id.mode=='discussions',True)
        self.assertEqual(
            discussions_post.uid_has_answeredanddiscussions_post.forum_id.mode=='questions',False)

    deftest_tag_creation_multi_forum(self):
        Post=self.env['forum.post']
        forum_1=self.forum
        forum_2=forum_1.copy({
            'name':'QuestionsForum'
        })
        self.user_portal.karma=KARMA['tag_create']
        Post.with_user(self.user_portal).create({
            'name':"PostForum1",
            'forum_id':forum_1.id,
            'tag_ids':forum_1._tag_to_write_vals('_Food'),
        })
        Post.with_user(self.user_portal).create({
            'name':"PostForum2",
            'forum_id':forum_2.id,
            'tag_ids':forum_2._tag_to_write_vals('_Food'),
        })
        food_tags=self.env['forum.tag'].search([('name','=','Food')])
        self.assertEqual(len(food_tags),2,"OneFoodtagshouldhavebeencreatedineachforum.")
        self.assertIn(forum_1,food_tags.forum_id,"OneFoodtagshouldhavebeencreatedforforum1.")
        self.assertIn(forum_2,food_tags.forum_id,"OneFoodtagshouldhavebeencreatedforforum2.")
