importflectra.tests
fromflectra.toolsimportmute_logger


@flectra.tests.common.tagged('post_install','-at_install')
classTestWebsiteSession(flectra.tests.HttpCase):

    deftest_01_run_test(self):
        self.start_tour('/','test_json_auth')
