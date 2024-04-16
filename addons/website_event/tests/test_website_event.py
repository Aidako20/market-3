#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website.tests.test_base_urlimportTestUrlCommon
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestUrlCanonical(TestUrlCommon):

    deftest_01_canonical_url(self):
        self._assertCanonical('/event?date=all',self.domain+'/event')
        self._assertCanonical('/event?date=old',self.domain+'/event?date=old')
