#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importdatetime

fromflectra.addons.gamification.tests.commonimportTransactionCaseGamification
fromflectra.exceptionsimportUserError
fromflectra.toolsimportmute_logger


classTestGamificationCommon(TransactionCaseGamification):

    defsetUp(self):
        super(TestGamificationCommon,self).setUp()
        employees_group=self.env.ref('base.group_user')
        self.user_ids=employees_group.users

        #Pushdemouserintothechallengebeforecreatinganewone
        self.env.ref('gamification.challenge_base_discover')._update_all()
        self.robot=self.env['res.users'].with_context(no_reset_password=True).create({
            'name':'R2D2',
            'login':'r2d2@openerp.com',
            'email':'r2d2@openerp.com',
            'groups_id':[(6,0,[employees_group.id])]
        })
        self.badge_good_job=self.env.ref('gamification.badge_good_job')


classtest_challenge(TestGamificationCommon):

    deftest_00_join_challenge(self):
        challenge=self.env.ref('gamification.challenge_base_discover')
        self.assertGreaterEqual(len(challenge.user_ids),len(self.user_ids),"Notenoughusersinbasechallenge")
        challenge._update_all()
        self.assertGreaterEqual(len(challenge.user_ids),len(self.user_ids)+1,"Thesearenotdroidsyouarelookingfor")

    deftest_10_reach_challenge(self):
        Goals=self.env['gamification.goal']
        challenge=self.env.ref('gamification.challenge_base_discover')

        challenge.state='inprogress'
        self.assertEqual(challenge.state,'inprogress',"Challengefailedthechangeofstate")

        goal_ids=Goals.search([('challenge_id','=',challenge.id),('state','!=','draft')])
        self.assertEqual(len(goal_ids),len(challenge.line_ids)*len(challenge.user_ids.ids),"Incorrectnumberofgoalsgenerated,shouldbe1goalperuser,perchallengeline")

        demo=self.user_demo
        #demouserwillsetatimezone
        demo.tz="Europe/Brussels"
        goal_ids=Goals.search([('user_id','=',demo.id),('definition_id','=',self.env.ref('gamification.definition_base_timezone').id)])

        goal_ids.update_goal()

        missed=goal_ids.filtered(lambdag:g.state!='reached')
        self.assertFalse(missed,"Noteverygoalwasreachedafterchangingtimezone")

        #rewardfortwofirstsasadminmayhavetimezone
        badge_id=self.badge_good_job.id
        challenge.write({'reward_first_id':badge_id,'reward_second_id':badge_id})
        challenge.state='done'

        badge_ids=self.env['gamification.badge.user'].search([('badge_id','=',badge_id),('user_id','=',demo.id)])
        self.assertEqual(len(badge_ids),1,"Demouserhasnotreceivedthebadge")

    @mute_logger('flectra.models.unlink')
    deftest_20_update_all_goals_filter(self):
        #Enrolltwointernalandtwoportalusersinthechallenge
        (
            portal_login_before_update,
            portal_login_after_update,
            internal_login_before_update,
            internal_login_after_update,
        )=all_test_users=self.env['res.users'].create([
            {
                'name':f'{kind}{age}login',
                'login':f'{kind}_{age}',
                'email':f'{kind}_{age}',
                'groups_id':[(6,0,groups_id)],
            }
            forkind,groups_idin(
                ('Portal',[]),
                ('Internal',[self.env.ref('base.group_user').id]),
            )
            foragein('Old','Recent')
        ])

        challenge=self.env.ref('gamification.challenge_base_discover')
        challenge.write({
            'state':'inprogress',
            'user_domain':False,
            'user_ids':[(6,0,all_test_users.ids)]
        })

        #Setupuseraccesslogs
        self.env['res.users.log'].search([('create_uid','in',challenge.user_ids.ids)]).unlink()
        now=datetime.datetime.now()

        #Create"old"loginrecords
        self.env['res.users.log'].create([
            {"create_uid":internal_login_before_update.id,'create_date':now-datetime.timedelta(minutes=3)},
            {"create_uid":portal_login_before_update.id,'create_date':now-datetime.timedelta(minutes=3)},
        ])

        #Resetgoalobjectivevalues
        all_test_users.partner_id.tz=False

        #Regenerateallgoals
        self.env["gamification.goal"].search([]).unlink()
        self.assertFalse(self.env['gamification.goal'].search([]))

        challenge.action_check()
        goal_ids=self.env['gamification.goal'].search(
            [('challenge_id','=',challenge.id),('state','!=','draft'),('user_id','in',challenge.user_ids.ids)]
        )
        self.assertEqual(len(goal_ids),4)
        self.assertEqual(set(goal_ids.mapped('state')),{'inprogress'})

        #Createmorerecentloginrecords
        self.env['res.users.log'].create([
            {"create_uid":internal_login_after_update.id,'create_date':now+datetime.timedelta(minutes=3)},
            {"create_uid":portal_login_after_update.id,'create_date':now+datetime.timedelta(minutes=3)},
        ])

        #Updategoalobjectivecheckedbygoaldefinition
        all_test_users.partner_id.write({'tz':'Europe/Paris'})

        #Updategoalsasdoneby_cron_update
        challenge._update_all()
        unchanged_goal_id=self.env['gamification.goal'].search([
            ('challenge_id','=',challenge.id),
            ('state','=','inprogress'), #otherswereupdatedto"reached"
            ('user_id','in',challenge.user_ids.ids),
        ])
        #Checkthateventhoughloginrecordforinternaluserisolderthangoalupdate,theirgoalwasreached.
        self.assertEqual(
            portal_login_before_update,
            unchanged_goal_id.user_id,
            "Onlyportaluserlastloggedinbeforelastchallengeupdateshouldnothavebeenupdated.",
        )


classtest_badge_wizard(TestGamificationCommon):

    deftest_grant_badge(self):
        wiz=self.env['gamification.badge.user.wizard'].create({
            'user_id':self.env.user.id,
            'badge_id':self.badge_good_job.id,
        })
        withself.assertRaises(UserError,msg="Ausercannotgrantabadgetohimself"):
            wiz.action_grant_badge()
        wiz.user_id=self.robot.id
        self.assertTrue(wiz.action_grant_badge(),"Couldnotgrantbadge")

        self.assertEqual(self.badge_good_job.stat_this_month,1)
