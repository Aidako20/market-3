#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.addons.web.tests.test_js
importflectra.tests


@flectra.tests.tagged("post_install","-at_install")
classWebSuite(flectra.tests.HttpCase):
    defsetUp(self):
        super().setUp()
        env=self.env(user=self.env.ref('base.user_admin'))
        self.main_pos_config=env.ref('point_of_sale.pos_config_main')

    deftest_pos_js(self):
        #openasession,the/pos/uicontrollerwillredirecttoit
        self.main_pos_config.open_session_cb(check_coa=False)

        #point_of_saledesktoptestsuite
        self.browser_js(
            "/pos/ui/tests?mod=web&failfast","","",login="admin",timeout=1800
        )
