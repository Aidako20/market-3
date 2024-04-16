#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale_coupon.tests.test_program_numbersimportTestSaleCouponProgramNumbers
fromflectra.addons.website.toolsimportMockRequest
fromflectra.exceptionsimportUserError
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestSaleCouponMultiwebsite(TestSaleCouponProgramNumbers):

    defsetUp(self):
        super(TestSaleCouponMultiwebsite,self).setUp()
        self.website=self.env['website'].browse(1)
        self.website2=self.env['website'].create({'name':'website2'})

    deftest_01_multiwebsite_checks(self):
        """Ensurethemultiwebsitecomplianceofprogramsandcoupons,bothin
            backendandfrontend.
        """
        order=self.empty_order
        self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        def_remove_reward():
            order.order_line.filtered('is_reward_line').unlink()
            self.assertEqual(len(order.order_line.ids),1,"Programshouldhavebeenremoved")

        def_apply_code(code,backend=True):
            ifbackend:
                self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                    'coupon_code':code
                }).process_coupon()
            else:
                self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,code)

        #==========================================
        #==========Programs(withcode)==========
        #==========================================

        #1.Backend-Generic
        _apply_code(self.p1.promo_code)
        self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisagenericpromoprogram")
        _remove_reward()

        #2.Frontend-Generic
        withMockRequest(self.env,website=self.website):
            _apply_code(self.p1.promo_code,False)
            self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisagenericpromoprogram(2)")
            _remove_reward()

        #makeprogramspecific
        self.p1.website_id=self.website.id
        #3.Backend-Specific
        withself.assertRaises(UserError):
            _apply_code(self.p1.promo_code) #theorderhasnowebsite_idsonotpossibletouseawebsitespecificcode

        #4.Frontend-Specific-Correctwebsite
        order.website_id=self.website.id
        withMockRequest(self.env,website=self.website):
            _apply_code(self.p1.promo_code,False)
            self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisaspecificpromoprogramforthecorrectwebsite")
            _remove_reward()

        #5.Frontend-Specific-Wrongwebsite
        self.p1.website_id=self.website2.id
        withMockRequest(self.env,website=self.website):
            _apply_code(self.p1.promo_code,False)
            self.assertEqual(len(order.order_line.ids),1,"Shouldnotgettherewardaswrongwebsite")

        #==============================
        #===========Coupons==========
        #==============================

        order.website_id=False
        self.env['coupon.generate.wizard'].with_context(active_id=self.discount_coupon_program.id).create({
            'nbr_coupons':4,
        }).generate_coupon()
        coupons=self.discount_coupon_program.coupon_ids

        #1.Backend-Generic
        _apply_code(coupons[0].code)
        self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisagenericcouponprogram")
        _remove_reward()

        #2.Frontend-Generic
        withMockRequest(self.env,website=self.website):
            _apply_code(coupons[1].code,False)
            self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisagenericcouponprogram(2)")
            _remove_reward()

        #makeprogramspecific
        self.discount_coupon_program.website_id=self.website.id
        #3.Backend-Specific
        withself.assertRaises(UserError):
            _apply_code(coupons[2].code) #theorderhasnowebsite_idsonotpossibletouseawebsitespecificcode

        #4.Frontend-Specific-Correctwebsite
        order.website_id=self.website.id
        withMockRequest(self.env,website=self.website):
            _apply_code(coupons[2].code,False)
            self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisaspecificcouponprogramforthecorrectwebsite")
            _remove_reward()

        #5.Frontend-Specific-Wrongwebsite
        self.discount_coupon_program.website_id=self.website2.id
        withMockRequest(self.env,website=self.website):
            _apply_code(coupons[3].code,False)
            self.assertEqual(len(order.order_line.ids),1,"Shouldnotgettherewardaswrongwebsite")

        #========================================
        #==========Programs(nocode)==========
        #========================================

        order.website_id=False
        self.p1.website_id=False
        self.p1.promo_code=False
        self.p1.promo_code_usage='no_code_needed'

        #1.Backend-Generic
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisagenericpromoprogram")

        #2.Frontend-Generic
        withMockRequest(self.env,website=self.website):
            order.recompute_coupon_lines()
            self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisagenericpromoprogram(2)")

        #makeprogramspecific
        self.p1.website_id=self.website.id
        #3.Backend-Specific
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Theorderhasnowebsite_idsonotpossibletouseawebsitespecificcode")

        #4.Frontend-Specific-Correctwebsite
        order.website_id=self.website.id
        withMockRequest(self.env,website=self.website):
            order.recompute_coupon_lines()
            self.assertEqual(len(order.order_line.ids),2,"Shouldgetthediscountlineasitisaspecificpromoprogramforthecorrectwebsite")

        #5.Frontend-Specific-Wrongwebsite
        self.p1.website_id=self.website2.id
        withMockRequest(self.env,website=self.website):
            order.recompute_coupon_lines()
            self.assertEqual(len(order.order_line.ids),1,"Shouldnotgettherewardaswrongwebsite")
