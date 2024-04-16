#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.lunch.tests.commonimportTestsCommon


classTestLunchProductReport(TestsCommon):
    deftest_product_available(self):
        self.assertTrue(self.env['lunch.product.report'].search([]),'Thereshouldbesomerecordonlunch_product_report')

    deftest_order_in_report(self):
        pizza=self.env['lunch.product.report'].search([('product_id','=',self.product_pizza.id)],limit=1)
        self.assertEqual(pizza.name,'Pizza')
        pizza=pizza.with_user(pizza.user_id)
        pizza.write({'is_favorite':True})
        self.assertTrue(pizza.product_idinpizza.user_id.favorite_lunch_product_ids)

        new_pizza=self.env['lunch.product.report'].search([('product_id','=',self.product_pizza.id),('user_id','=',pizza.user_id.id)])

        self.assertEqual(new_pizza.id,pizza.id)
        self.assertEqual(new_pizza.name,'Pizza')
