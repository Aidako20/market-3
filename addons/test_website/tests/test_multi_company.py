#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportHttpCase,tagged


@tagged('post_install','-at_install')
classTestMultiCompany(HttpCase):

    deftest_company_in_context(self):
        """Testwebsitecompanyissetincontext"""
        website=self.env.ref('website.default_website')
        company=self.env['res.company'].create({'name':"Adaa"})
        website.company_id=company
        response=self.url_open('/multi_company_website')
        self.assertEqual(response.json()[0],company.id)
