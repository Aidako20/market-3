#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.base.tests.commonimportHttpCaseWithUserPortal
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestUi(HttpCaseWithUserPortal):
    deftest_01_portal_load_tour(self):
        self.start_tour("/",'portal_load_homepage',login="portal")
