#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website.tests.test_performanceimportUtilPerf


classTestPerformance(UtilPerf):
    deftest_10_perf_sql_website_controller_minimalist(self):
        url='/empty_controller_test'
        self.assertEqual(self._get_url_hot_query(url),3)
