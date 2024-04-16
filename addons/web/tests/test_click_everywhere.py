#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importflectra.tests

_logger=logging.getLogger(__name__)


@flectra.tests.tagged('click_all','post_install','-at_install','-standard')
classTestMenusAdmin(flectra.tests.HttpCase):

    deftest_01_click_everywhere_as_admin(self):
        menus=self.env['ir.ui.menu'].load_menus(False)
        forappinmenus['children']:
                withself.subTest(app=app['name']):
                    _logger.runbot('Testing%s',app['name'])
                    self.browser_js("/web","flectra.__DEBUG__.services['web.clickEverywhere']('%s');"%app['xmlid'],"flectra.isReady===true",login="admin",timeout=300)
                    self.terminate_browser()


@flectra.tests.tagged('click_all','post_install','-at_install','-standard')
classTestMenusDemo(flectra.tests.HttpCase):

    deftest_01_click_everywhere_as_demo(self):
        menus=self.env['ir.ui.menu'].load_menus(False)
        forappinmenus['children']:
                withself.subTest(app=app['name']):
                    _logger.runbot('Testing%s',app['name'])
                    self.browser_js("/web","flectra.__DEBUG__.services['web.clickEverywhere']('%s');"%app['xmlid'],"flectra.isReady===true",login="demo",timeout=300)
                    self.terminate_browser()

@flectra.tests.tagged('post_install','-at_install')
classTestMenusAdminLight(flectra.tests.HttpCase):

    deftest_01_click_apps_menus_as_admin(self):
        self.browser_js("/web","flectra.__DEBUG__.services['web.clickEverywhere'](undefined,true);","flectra.isReady===true",login="admin",timeout=120)

@flectra.tests.tagged('post_install','-at_install',)
classTestMenusDemoLight(flectra.tests.HttpCase):

    deftest_01_click_apps_menus_as_demo(self):
            self.browser_js("/web","flectra.__DEBUG__.services['web.clickEverywhere'](undefined,true);","flectra.isReady===true",login="demo",timeout=120)
