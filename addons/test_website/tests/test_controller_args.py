#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importflectra.tests


@flectra.tests.common.tagged('post_install','-at_install')
classTestWebsiteControllerArgs(flectra.tests.HttpCase):

    deftest_crawl_args(self):
        req=self.url_open('/ignore_args/converter/valueA/?b=valueB&c=valueC')
        self.assertEqual(req.status_code,200)
        self.assertEqual(req.json(),{'a':'valueA','b':'valueB','kw':{'c':'valueC'}})

        req=self.url_open('/ignore_args/converter/valueA/nokw?b=valueB&c=valueC')
        self.assertEqual(req.status_code,200)
        self.assertEqual(req.json(),{'a':'valueA','b':'valueB'})

        req=self.url_open('/ignore_args/converteronly/valueA/?b=valueB&c=valueC')
        self.assertEqual(req.status_code,200)
        self.assertEqual(req.json(),{'a':'valueA','kw':None})

        req=self.url_open('/ignore_args/none?a=valueA&b=valueB')
        self.assertEqual(req.status_code,200)
        self.assertEqual(req.json(),{'a':None,'kw':None})

        req=self.url_open('/ignore_args/a?a=valueA&b=valueB')
        self.assertEqual(req.status_code,200)
        self.assertEqual(req.json(),{'a':'valueA','kw':None})

        req=self.url_open('/ignore_args/kw?a=valueA&b=valueB')
        self.assertEqual(req.status_code,200)
        self.assertEqual(req.json(),{'a':'valueA','kw':{'b':'valueB'}})
