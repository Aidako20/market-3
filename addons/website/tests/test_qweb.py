#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxmlimportetree
importre

fromflectraimporthttp,tools
fromflectra.addons.base.tests.commonimportTransactionCaseWithUserDemo
fromflectra.addons.website.toolsimportMockRequest
fromflectra.modules.moduleimportget_module_resource
fromflectra.tests.commonimportTransactionCase


classTestQweb(TransactionCaseWithUserDemo):
    def_load(self,module,*args):
        tools.convert_file(self.cr,'website',
                           get_module_resource(module,*args),
                           {},'init',False,'test')

    deftest_qweb_cdn(self):
        self._load('website','tests','template_qweb_test.xml')

        website=self.env.ref('website.default_website')
        website.write({
            "cdn_activated":True,
            "cdn_url":"http://test.cdn"
        })

        demo=self.env['res.users'].search([('login','=','demo')])[0]
        demo.write({"signature":'''<spanclass="toto">
                span<spanclass="fa"></span><imgsrc="/web/image/1"/>
            </span>'''})

        demo_env=self.env(user=demo)

        html=demo_env['ir.qweb']._render('website.test_template',{"user":demo},website_id=website.id)
        asset_data=etree.HTML(html).xpath('//*[@data-asset-xmlid]')[0]
        asset_xmlid=asset_data.attrib.get('data-asset-xmlid')
        asset_version=asset_data.attrib.get('data-asset-version')

        html=html.strip().decode('utf8')
        html=re.sub(r'\?unique=[^"]+','',html).encode('utf8')

        attachments=demo_env['ir.attachment'].search([('url','=like','/web/content/%-%/website.test_bundle.%')])
        self.assertEqual(len(attachments),2)

        format_data={
            "js":attachments[0].url,
            "css":attachments[1].url,
            "user_id":demo.id,
            "filename":"Marc%20Demo",
            "alt":"MarcDemo",
            "asset_xmlid":asset_xmlid,
            "asset_version":asset_version,
        }

        self.assertEqual(html,("""<!DOCTYPEhtml>
<html>
    <head>
        <linkrel="stylesheet"href="http://test.external.link/style1.css"/>
        <linkrel="stylesheet"href="http://test.external.link/style2.css"/>
        <linktype="text/css"rel="stylesheet"href="http://test.cdn%(css)s"data-asset-xmlid="%(asset_xmlid)s"data-asset-version="%(asset_version)s"/>
        <meta/>
        <scripttype="text/javascript"src="http://test.external.link/javascript1.js"></script>
        <scripttype="text/javascript"src="http://test.external.link/javascript2.js"></script>
        <scripttype="text/javascript"src="http://test.cdn%(js)s"data-asset-xmlid="%(asset_xmlid)s"data-asset-version="%(asset_version)s"></script>
    </head>
    <body>
        <imgsrc="http://test.external.link/img.png"loading="lazy"/>
        <imgsrc="http://test.cdn/website/static/img.png"loading="lazy"/>
        <ahref="http://test.external.link/link">x</a>
        <ahref="http://test.cdn/web/content/local_link">x</a>
        <spanstyle="background-image:url('http://test.cdn/web/image/2')">xxx</span>
        <divwidget="html"><spanclass="toto">
                span<spanclass="fa"></span><imgsrc="http://test.cdn/web/image/1"loading="lazy">
            </span></div>
        <divwidget="image"><imgsrc="http://test.cdn/web/image/res.users/%(user_id)s/image_1920/%(filename)s"class="imgimg-fluid"alt="%(alt)s"loading="lazy"/></div>
    </body>
</html>"""%format_data).encode('utf8'))


classTestQwebProcessAtt(TransactionCase):
    defsetUp(self):
        super(TestQwebProcessAtt,self).setUp()
        self.website=self.env.ref('website.default_website')
        self.env['res.lang']._activate_lang('fr_FR')
        self.website.language_ids=self.env.ref('base.lang_en')+self.env.ref('base.lang_fr')
        self.website.default_lang_id=self.env.ref('base.lang_en')
        self.website.cdn_activated=True
        self.website.cdn_url="http://test.cdn"
        self.website.cdn_filters="\n".join(["^(/[a-z]{2}_[A-Z]{2})?/a$","^(/[a-z]{2})?/a$","^/b$"])

    def_test_att(self,url,expect,tag='a',attribute='href'):
        self.assertEqual(
            self.env['ir.qweb']._post_processing_att(tag,{attribute:url},{}),
            expect
        )

    deftest_process_att_no_request(self):
        #norequestsonoURLrewriting
        self._test_att('/',{'href':'/'})
        self._test_att('/en/',{'href':'/en/'})
        self._test_att('/fr/',{'href':'/fr/'})
        #noURLrewrittingforCDN
        self._test_att('/a',{'href':'/a'})

    deftest_process_att_no_website(self):
        withMockRequest(self.env):
            #nowebsitesoURLrewriting
            self._test_att('/',{'href':'/'})
            self._test_att('/en/',{'href':'/en/'})
            self._test_att('/fr/',{'href':'/fr/'})
            #noURLrewrittingforCDN
            self._test_att('/a',{'href':'/a'})

    deftest_process_att_monolang_route(self):
        withMockRequest(self.env,website=self.website,multilang=False):
            #langnotchangedinURLbutCDNenabled
            self._test_att('/a',{'href':'http://test.cdn/a'})
            self._test_att('/en/a',{'href':'http://test.cdn/en/a'})
            self._test_att('/b',{'href':'http://test.cdn/b'})
            self._test_att('/en/b',{'href':'/en/b'})

    deftest_process_att_no_request_lang(self):
        withMockRequest(self.env,website=self.website):
            self._test_att('/',{'href':'/'})
            self._test_att('/en/',{'href':'/'})
            self._test_att('/fr/',{'href':'/fr/'})

    deftest_process_att_with_request_lang(self):
        withMockRequest(self.env,website=self.website,context={'lang':'fr_FR'}):
            self._test_att('/',{'href':'/fr/'})
            self._test_att('/en/',{'href':'/'})
            self._test_att('/fr/',{'href':'/fr/'})

    deftest_process_att_matching_cdn_and_lang(self):
        withMockRequest(self.env,website=self.website):
            #langprefixisaddedbeforeCDN
            self._test_att('/a',{'href':'http://test.cdn/a'})
            self._test_att('/en/a',{'href':'http://test.cdn/a'})
            self._test_att('/fr/a',{'href':'http://test.cdn/fr/a'})
            self._test_att('/b',{'href':'http://test.cdn/b'})
            self._test_att('/en/b',{'href':'http://test.cdn/b'})
            self._test_att('/fr/b',{'href':'/fr/b'})

    deftest_process_att_no_route(self):
        withMockRequest(self.env,website=self.website,context={'lang':'fr_FR'},routing=False):
            #defaultonmultilang=Trueifrouteisnot/{module}/static/
            self._test_att('/web/static/hi',{'href':'/web/static/hi'})
            self._test_att('/my-page',{'href':'/fr/my-page'})

    deftest_process_att_url_crap(self):
        withMockRequest(self.env,website=self.website):
            match=http.root.get_db_router.return_value.bind.return_value.match
            ##{fragment}isstrippedfromURLwhentestingroute
            self._test_att('/x#y?z',{'href':'/x#y?z'})
            match.assert_called_with('/x',method='POST',query_args=None)

            match.reset_calls()
            self._test_att('/x?y#z',{'href':'/x?y#z'})
            match.assert_called_with('/x',method='POST',query_args='y')
