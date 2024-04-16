#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

fromlxmlimportetree
fromunittest.mockimportpatch

fromflectra.testsimportcommon


classMockLinkTracker(common.BaseCase):

    defsetUp(self):
        super(MockLinkTracker,self).setUp()

        def_get_title_from_url(url):
            return"Test_TITLE"

        link_tracker_title_patch=patch('flectra.addons.link_tracker.models.link_tracker.LinkTracker._get_title_from_url',wraps=_get_title_from_url)
        link_tracker_title_patch.start()
        self.addCleanup(link_tracker_title_patch.stop)

    def_get_href_from_anchor_id(self,body,anchor_id):
        """ParseenhtmlbodytofindthehrefofanelementgivenitsID."""
        html=etree.fromstring(body,parser=etree.HTMLParser())
        returnhtml.xpath("//*[@id='%s']"%anchor_id)[0].attrib.get('href')

    def_get_tracker_from_short_url(self,short_url):
        code=self.env['link.tracker.code'].sudo().search([
            ('code','=',short_url.split('/r/')[-1])
        ])
        returncode.link_id

    defassertLinkShortenedHtml(self,body,link_info,link_params=None):
        """FindshortenedlinksinanHTMLcontent.Usage:

        self.assertLinkShortenedHtml(
            message.body,
            ('url0','http://www.flectrahq.com', True),
            {'utm_campaign':self.utm_c.name,'utm_medium':self.utm_m.name}
        )
        """
        (anchor_id,url,is_shortened)=link_info
        anchor_href=self._get_href_from_anchor_id(body,anchor_id)
        ifis_shortened:
            self.assertTrue('/r/'inanchor_href,'%sshouldbeshortened:%s'%(anchor_id,anchor_href))
            link_tracker=self._get_tracker_from_short_url(anchor_href)
            self.assertEqual(url,link_tracker.url)
            self.assertLinkParams(url,link_tracker,link_params=link_params)
        else:
            self.assertTrue('/r/'notinanchor_href,'%sshouldnotbeshortened:%s'%(anchor_id,anchor_href))
            self.assertEqual(anchor_href,url)

    defassertLinkShortenedText(self,body,link_info,link_params=None):
        """Findshortenedlinksinantextcontent.Usage:

        self.assertLinkShortenedText(
            message.body,
            ('http://www.flectrahq.com', True),
            {'utm_campaign':self.utm_c.name,'utm_medium':self.utm_m.name}
        )
        """
        (url,is_shortened)=link_info
        link_tracker=self.env['link.tracker'].search([('url','=',url)])
        ifis_shortened:
            self.assertEqual(len(link_tracker),1)
            self.assertIn(link_tracker.short_url,body,'%sshouldbeshortened'%(url))
            self.assertLinkParams(url,link_tracker,link_params=link_params)
        else:
            self.assertEqual(len(link_tracker),0)
            self.assertIn(url,body)

    defassertLinkParams(self,url,link_tracker,link_params=None):
        """Usage

        self.assertLinkTracker(
            'http://www.example.com',
            link_tracker,
            {'utm_campaign':self.utm_c.name,'utm_medium':self.utm_m.name}
        )
        """
        #checkUTMSarecorrectlysetonredirectURL
        original_url=werkzeug.urls.url_parse(url)
        redirect_url=werkzeug.urls.url_parse(link_tracker.redirected_url)
        redirect_params=redirect_url.decode_query().to_dict(flat=True)
        self.assertEqual(redirect_url.scheme,original_url.scheme)
        self.assertEqual(redirect_url.decode_netloc(),original_url.decode_netloc())
        self.assertEqual(redirect_url.path,original_url.path)
        iflink_params:
            self.assertEqual(redirect_params,link_params)
