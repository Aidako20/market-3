#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.sale_coupon.tests.commonimportTestSaleCouponCommon
fromflectra.exceptionsimportUserError
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestSaleInvoicing(TestSaleCouponCommon):

    deftest_invoicing_order_with_promotions(self):
        discount_coupon_program=self.env['coupon.program'].create({
            'name':'10%Discount',#Defaultbehavior
            'program_type':'coupon_program',
            'reward_type':'discount',
            'discount_apply_on':'on_order',
            'promo_code_usage':'no_code_needed',
        })
        #Overridethedefaultinvoice_policyonproducts
        discount_coupon_program.discount_line_product_id.invoice_policy='order'
        product=self.env['product.product'].create({
            'invoice_policy':'delivery',
            'name':'Productinvoicedondelivery',
            'lst_price':500,
        })

        order=self.empty_order
        order.write({
            'order_line':[
                (0,0,{
                    'product_id':product.id,
                })
            ]
        })

        order.recompute_coupon_lines()
        #Orderisnotconfirmed,thereshouldn'tbeanyinvoiceableline
        invoiceable_lines=order._get_invoiceable_lines()
        self.assertEqual(len(invoiceable_lines),0)

        order.action_confirm()
        invoiceable_lines=order._get_invoiceable_lines()
        #Productwasnotdelivered,wecannotinvoice
        #theproductlinenorthepromotionline
        self.assertEqual(len(invoiceable_lines),0)
        withself.assertRaises(UserError):
            order._create_invoices()

        order.order_line[0].qty_delivered=1
        #Productisdelivered,thetwolinescanbeinvoiced.
        invoiceable_lines=order._get_invoiceable_lines()
        self.assertEqual(order.order_line,invoiceable_lines)
        account_move=order._create_invoices()
        self.assertEqual(len(account_move.invoice_line_ids),2)

    deftest_coupon_on_order_sequence(self):
        #discount_coupon_program
        self.env['coupon.program'].create({
            'name':'10%Discount',#Defaultbehavior
            'program_type':'coupon_program',
            'reward_type':'discount',
            'discount_apply_on':'on_order',
            'promo_code_usage':'no_code_needed',
        })
        order=self.empty_order

        #orderline1
        self.env['sale.order.line'].create({
            'product_id':self.env.ref('product.product_product_6').id,
            'name':'largeCabinet',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line),2,'Couponcorrectlyapplied')

        #orderline2
        self.env['sale.order.line'].create({
            'product_id':self.env.ref('product.product_product_11').id,
            'name':'conferenceChair',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line),3,'Couponcorrectlyapplied')

        self.assertTrue(order.order_line.sorted(lambdax:x.sequence)[-1].is_reward_line,'Globalcouponsappearonthelastline')
