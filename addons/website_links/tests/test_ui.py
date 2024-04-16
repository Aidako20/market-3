#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

importflectra.tests


@flectra.tests.common.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    defsetUp(self):
        super(TestUi,self).setUp()

        def_get_title_from_url(addr,**kw):
            return'ContactUs|MyWebsite'

        patcher=patch('flectra.addons.link_tracker.models.link_tracker.LinkTracker._get_title_from_url',wraps=_get_title_from_url)
        patcher.start()
        self.addCleanup(patcher.stop)

    deftest_01_test_ui(self):
        self.env['link.tracker'].create({
            'campaign_id':2,
            'medium_id':2,
            'source_id':2,
            'url':self.env["ir.config_parameter"].sudo().get_param("web.base.url")+'/contactus',
        })
        self.start_tour("/",'website_links_tour',login="admin")
