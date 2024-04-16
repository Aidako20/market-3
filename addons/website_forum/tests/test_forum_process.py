#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.gamification.tests.commonimportHttpCaseGamification
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestUi(HttpCaseGamification):

    deftest_01_admin_forum_tour(self):
        self.start_tour("/",'question',login="admin",step_delay=100)

    deftest_02_demo_question(self):
        forum=self.env.ref('website_forum.forum_help')
        demo=self.user_demo
        demo.karma=forum.karma_post+1
        self.start_tour("/",'forum_question',login="demo")
