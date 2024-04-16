#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.http_routing.models.ir_httpimporturl_lang
fromflectra.addons.website.toolsimportMockRequest
fromflectra.testsimportHttpCase,tagged


@tagged('-at_install','post_install')
classTestLangUrl(HttpCase):
    defsetUp(self):
        super(TestLangUrl,self).setUp()

        #Simulatemultilangwithoutloadingtranslations
        self.website=self.env.ref('website.default_website')
        self.lang_fr=self.env['res.lang']._activate_lang('fr_FR')
        self.lang_fr.write({'url_code':'fr'})
        self.website.language_ids=self.env.ref('base.lang_en')+self.lang_fr
        self.website.default_lang_id=self.env.ref('base.lang_en')

    deftest_01_url_lang(self):
        withMockRequest(self.env,website=self.website):
            self.assertEqual(url_lang('','[lang]'),'/[lang]/hello',"`[lang]`isusedtobereplacedintheurl_returnafterinstallingalanguage,itshouldnotbereplacedorremoved.")

    deftest_02_url_redirect(self):
        url='/fr_WHATEVER/contactus'
        r=self.url_open(url)
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.url.endswith('/fr/contactus'),"fr_WHATEVERshouldbeforwardedto'fr_FR'langasclosestmatch")

        url='/fr_FR/contactus'
        r=self.url_open(url)
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.url.endswith('/fr/contactus'),"langinurlshoulduseurl_code('fr'inthiscase)")

    deftest_03_url_cook_lang_not_available(self):
        """Anactivatedres.langshouldnotbedisplayedinthefrontendifnotawebsitelang."""
        self.website.language_ids=self.env.ref('base.lang_en')
        r=self.url_open('/fr/contactus')
        self.assertTrue('lang="en-US"'inr.text,"frenchshouldnotbedisplayedasnotafrontendlang")

    deftest_04_url_cook_lang_not_available(self):
        """`nearest_lang`shouldfilteroutlangnotavailableinfrontend.
        Eg:1.goinbackendinenglish->request.context['lang']=`en_US`
            2.goinfrontend,therequest.context['lang']ispassedthrough
               `nearest_lang`whichshouldnotreturnenglish.Morethena
               misbehavioritwillcrashinwebsitelanguageselectortemplate.
        """
        #1.Loadbackend
        self.authenticate('admin','admin')
        r=self.url_open('/web')
        self.assertTrue('"lang":"en_US"'inr.text,"ensureenglishwasloaded")

        #2.Removeen_USfromfrontend
        self.website.language_ids=self.lang_fr
        self.website.default_lang_id=self.lang_fr

        #3.Ensurevisiting/contactusdonotcrash
        url='/contactus'
        r=self.url_open(url)
        self.assertEqual(r.status_code,200)
        self.assertTrue('lang="fr-FR"'inr.text,"Ensurecontactusdidnotsoftcrash+loadedincorrectlang")

    deftest_05_reroute_unicode(self):
        res=self.url_open('/fr/привет')
        self.assertEqual(res.status_code,404,"Reroutingdidn'tcrashbecauseofnonlatin-1characters")
