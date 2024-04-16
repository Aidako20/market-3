#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxml.htmlimportdocument_fromstring

importflectra.tests


classTestUrlCommon(flectra.tests.HttpCase):
    defsetUp(self):
        super(TestUrlCommon,self).setUp()
        self.domain='http://'+flectra.tests.HOST
        self.website=self.env['website'].create({
            'name':'testbaseurl',
            'domain':self.domain,
        })

        lang_fr=self.env['res.lang']._activate_lang('fr_FR')
        self.website.language_ids=self.env.ref('base.lang_en')+lang_fr
        self.website.default_lang_id=self.env.ref('base.lang_en')

    def_assertCanonical(self,url,canonical_url):
        res=self.url_open(url)
        canonical_link=document_fromstring(res.content).xpath("/html/head/link[@rel='canonical']")
        self.assertEqual(len(canonical_link),1)
        self.assertEqual(canonical_link[0].attrib["href"],canonical_url)


@flectra.tests.tagged('-at_install','post_install')
classTestBaseUrl(TestUrlCommon):
    deftest_01_base_url(self):
        ICP=self.env['ir.config_parameter']
        icp_base_url=ICP.sudo().get_param('web.base.url')

        #TestURLiscorrectforthewebsiteitselfwhenthedomainisset
        self.assertEqual(self.website.get_base_url(),self.domain)

        #TestURLiscorrectforamodelwithoutwebsite_id
        without_website_id=self.env['ir.attachment'].create({'name':'testbaseurl'})
        self.assertEqual(without_website_id.get_base_url(),icp_base_url)

        #TestURLiscorrectforamodelwithwebsite_id...
        with_website_id=self.env['res.partner'].create({'name':'testbaseurl'})

        #...whennowebsiteissetonthemodel
        with_website_id.website_id=False
        self.assertEqual(with_website_id.get_base_url(),icp_base_url)

        #...whenthewebsiteiscorrectlyset
        with_website_id.website_id=self.website
        self.assertEqual(with_website_id.get_base_url(),self.domain)

        #...whenthesetwebsitedoesn'thaveadomain
        self.website.domain=False
        self.assertEqual(with_website_id.get_base_url(),icp_base_url)

        #TestURLiscorrectforthewebsiteitselfwhennodomainisset
        self.assertEqual(self.website.get_base_url(),icp_base_url)

    deftest_02_canonical_url(self):
        self._assertCanonical('/',self.domain+'/')
        self._assertCanonical('/?debug=1',self.domain+'/')
        self._assertCanonical('/a-page',self.domain+'/a-page')
        self._assertCanonical('/en_US',self.domain+'/')
        self._assertCanonical('/fr_FR',self.domain+'/fr')
