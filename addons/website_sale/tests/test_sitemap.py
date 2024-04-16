#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportHttpCase,tagged


@tagged('post_install','-at_install')
classTestSitemap(HttpCase):

    defsetUp(self):
        super(TestSitemap,self).setUp()

        self.cats=self.env['product.public.category'].create([{
            'name':'Level0',
        },{
            'name':'Level1',
        },{
            'name':'Level2',
        }])
        self.cats[2].parent_id=self.cats[1].id
        self.cats[1].parent_id=self.cats[0].id

    deftest_01_shop_route_sitemap(self):
        resp=self.url_open('/sitemap.xml')
        level2_url='/shop/category/level-0-level-1-level-2-%s'%self.cats[2].id
        self.assertTrue(level2_urlinresp.text,"Categoryentryinsitemapshouldbeprefixedbyitsparenthierarchy.")
