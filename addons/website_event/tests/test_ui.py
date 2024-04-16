#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests
fromflectraimporttools


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):
    deftest_admin(self):
        self.start_tour("/",'event',login='admin',step_delay=100)
