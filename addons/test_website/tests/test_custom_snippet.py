#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests
fromflectra.toolsimportmute_logger


@flectra.tests.common.tagged('post_install','-at_install')
classTestCustomSnippet(flectra.tests.HttpCase):

    @mute_logger('flectra.addons.http_routing.models.ir_http','flectra.http')
    deftest_01_run_tour(self):
        self.start_tour("/",'test_custom_snippet',login="admin")
