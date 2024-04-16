#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale_coupon.tests.commonimportTestSaleCouponCommon
fromflectra.exceptionsimportUserError
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestSaleCouponMultiCompany(TestSaleCouponCommon):

    defsetUp(self):
        super(TestSaleCouponMultiCompany,self).setUp()

        self.company_a=self.env.company
        self.company_b=self.env['res.company'].create(dict(name="TEST"))

        self.immediate_promotion_program_c2=self.env['coupon.program'].create({
            'name':'BuyA+1B,1Barefree',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'reward_product_id':self.product_B.id,
            'rule_products_domain':"[('id','in',[%s])]"%(self.product_A.id),
            'active':True,
            'company_id':self.company_b.id,
        })

    deftest_applicable_programs(self):

        order=self.empty_order
        order.write({'order_line':[
            (0,False,{
                'product_id':self.product_A.id,
                'name':'1ProductA',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            }),
            (0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        order.recompute_coupon_lines()

        def_get_applied_programs(order):
            #temporarycopyofsale_order._get_applied_programs
            #toensureeachcommitstaysindependent
            #canbelaterremovedandreplacedinmaster.
            returnorder.code_promo_program_id+order.no_code_promo_program_ids+order.applied_coupon_ids.mapped('program_id')

        self.assertNotIn(self.immediate_promotion_program_c2,order._get_applicable_programs())
        self.assertNotIn(self.immediate_promotion_program_c2,_get_applied_programs(order))

        order_b=self.env["sale.order"].create({
            'company_id':self.company_b.id,
            'partner_id':order.partner_id.id,
        })
        order_b.write({'order_line':[
            (0,False,{
                'product_id':self.product_A.id,
                'name':'1ProductA',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            }),
            (0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        self.assertNotIn(self.immediate_promotion_program,order_b._get_applicable_programs())

        order_b.recompute_coupon_lines()
        self.assertIn(self.immediate_promotion_program_c2,_get_applied_programs(order_b))
        self.assertNotIn(self.immediate_promotion_program,_get_applied_programs(order_b))
