#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale_coupon.tests.commonimportTestSaleCouponCommon


classTestProgramWithoutCodeOperations(TestSaleCouponCommon):
    #Testsomebasicoperation(create,write,unlink)onanimmediatecouponprogramonwhichweshould
    #applyorremovetherewardautomatically,asthere'snoprogramcode.

    deftest_immediate_program_basic_operation(self):

        #2productsAareneeded
        self.immediate_promotion_program.write({'rule_min_quantity':2.0})
        order=self.empty_order
        #Testcase1(1A):Assertthatnorewardisgiven,astheproductBismissing
        order.write({'order_line':[
            (0,False,{
                'product_id':self.product_A.id,
                'name':'1ProductA',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Thepromooffershouldn'thavebeenappliedastheproductBisn'tintheorder")

        #Testcase2(1A1B):Assertthatnorewardisgiven,astheproductBisnotpresentinthecorrectquantity
        order.write({'order_line':[
            (0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffershouldn'thavebeenappliedas2productAaren'tintheorder")

        #Testcase3(2A1B):AssertthattherewardisgivenastheproductBisnowintheorder
        order.write({'order_line':[(1,order.order_line[0].id,{'product_uom_qty':2.0})]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffertshouldhavebeenapplied,thediscountisnotcreated")

        #Testcase4(1A1B):Assertthattherewardisremovedaswedon'tbuy2productsBanymore
        order.write({'order_line':[(1,order.order_line[0].id,{'product_uom_qty':1.0})]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Thepromorewardshouldhavebeenremovedastherulesarenotmatchedanymore")
        self.assertEqual(order.order_line[0].product_id.id,self.product_A.id,"Thewronglinehasbeenremoved")
        self.assertEqual(order.order_line[1].product_id.id,self.product_B.id,"Thewronglinehasbeenremoved")

        #Testcase5(1B):Assertthattherewardisremovedwhentheorderismodifiedanddoesn'tmatchtherulesanymore
        order.write({'order_line':[
            (1,order.order_line[0].id,{'product_uom_qty':2.0}),
            (2,order.order_line[0].id,False)
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Thepromorewardshouldhavebeenremovedastherulesarenotmatchedanymore")
        self.assertEqual(order.order_line.product_id.id,self.product_B.id,"Thewronglinehasbeenremoved")
