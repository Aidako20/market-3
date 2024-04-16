#coding:utf-8
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.addons.website.toolsimportMockRequest
fromflectra.testsimportTransactionCase,tagged

@tagged('post_install','-at_install')
classWebsiteSaleVisitorTests(TransactionCase):

    defsetUp(self):
        super().setUp()
        self.website=self.env.ref('website.default_website')
        self.WebsiteSaleController=WebsiteSale()
        self.cookies={}

    deftest_create_visitor_on_tracked_product(self):
        self.WebsiteSaleController=WebsiteSale()
        existing_visitors=self.env['website.visitor'].search([])
        existing_tracks=self.env['website.track'].search([])

        product=self.env['product.product'].create({
            'name':'StorageBox',
            'website_published':True,
        })

        withMockRequest(self.env,website=self.website):
            self.cookies=self.WebsiteSaleController.products_recently_viewed_update(product.id)

        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        new_tracks=self.env['website.track'].search([('id','notin',existing_tracks.ids)])
        self.assertEqual(len(new_visitors),1,"Avisitorshouldbecreatedaftervisitingatrackedproduct")
        self.assertEqual(len(new_tracks),1,"Atrackshouldbecreatedaftervisitingatrackedproduct")

        withMockRequest(self.env,website=self.website,cookies=self.cookies):
            self.WebsiteSaleController.products_recently_viewed_update(product.id)

        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        new_tracks=self.env['website.track'].search([('id','notin',existing_tracks.ids)])
        self.assertEqual(len(new_visitors),1,"Novisitorshouldbecreatedaftervisitinganothertrackedproduct")
        self.assertEqual(len(new_tracks),1,"Notrackshouldbecreatedaftervisitingthesametrackedproductbefore30min")

        product=self.env['product.product'].create({
            'name':'LargeCabinet',
            'website_published':True,
            'list_price':320.0,
        })

        withMockRequest(self.env,website=self.website,cookies=self.cookies):
            self.WebsiteSaleController.products_recently_viewed_update(product.id)

        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        new_tracks=self.env['website.track'].search([('id','notin',existing_tracks.ids)])
        self.assertEqual(len(new_visitors),1,"Novisitorshouldbecreatedaftervisitinganothertrackedproduct")
        self.assertEqual(len(new_tracks),2,"Atrackshouldbecreatedaftervisitinganothertrackedproduct")

    deftest_recently_viewed_company_changed(self):
        #Testthat,bychangingthecompanyofatrackedproduct,therecentlyviewedproductdonotcrash
        new_company=self.env['res.company'].create({
            'name':'TestCompany',
        })
        public_user=self.env.ref('base.public_user')

        product=self.env['product.product'].create({
            'name':'TestProduct',
            'website_published':True,
            'sale_ok':True,
        })

        self.website=self.website.with_user(public_user).with_context(website_id=self.website.id)
        withMockRequest(self.website.env,website=self.website):
            self.cookies=self.WebsiteSaleController.products_recently_viewed_update(product.id)
        product.product_tmpl_id.company_id=new_company
        product.product_tmpl_id.flush(['company_id'],product.product_tmpl_id)
        withMockRequest(self.website.env,website=self.website,cookies=self.cookies):
            #Shouldnotraiseanerror
            res=self.WebsiteSaleController.products_recently_viewed()
            self.assertTrue('products'notinresorlen(res['products'])==0)
