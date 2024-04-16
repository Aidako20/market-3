#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectra.addons.sale_coupon.tests.commonimportTestSaleCouponCommon
fromflectra.exceptionsimportUserError
fromflectra.fieldsimportDate

classTestProgramRules(TestSaleCouponCommon):
    #Testallthevalidityrulestoallowacustomertohaveareward.
    #Thecheckbasedontheproductsisalreadydoneinthebasicoperationstest

    deftest_program_rules_partner_based(self):
        #Testcase:Basedonthepartnersdomain

        self.immediate_promotion_program.write({'rule_partners_domain':"[('id','in',[%s])]"%(self.steve.id)})

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
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffertshouldhavebeenappliedasthepartneriscorrect,thediscountisnotcreated")

        order=self.env['sale.order'].create({'partner_id':self.env['res.partner'].create({'name':'MyPartner'}).id})
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
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenapplied,thediscountiscreated")

    deftest_program_rules_minimum_purchased_amount(self):
        #Testcase:Basedontheminimumpurchased

        self.immediate_promotion_program.write({
            'rule_minimum_amount':1006,
            'rule_minimum_amount_tax_inclusion':'tax_excluded'
        })

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
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedasthepurchasedamountisnotenough")

        order=self.env['sale.order'].create({'partner_id':self.steve.id})
        order.write({'order_line':[
            (0,False,{
                'product_id':self.product_A.id,
                'name':'10ProductA',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':10.0,
            }),
            (0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        order.recompute_coupon_lines()
        #10*100+5=1005
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldnotbeappliedasthepurchasedamountisnotenough")

        self.immediate_promotion_program.rule_minimum_amount=1005
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffertshouldbeappliedasthepurchasedamountisnowenough")

        #10*(100*1.15)+(5*1.15)=10*115+5.75=1155.75
        self.immediate_promotion_program.rule_minimum_amount=1006
        self.immediate_promotion_program.rule_minimum_amount_tax_inclusion='tax_included'
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffertshouldbeappliedastheinitialamountrequiredisnowtaxincluded")

    deftest_program_rules_minimum_purchased_amount_and_free_product(self):
        #Testcases:Basedontheminimumpurchasedandfreeproduct
        self.immediate_promotion_program.write({
            'rule_minimum_amount':10,
            'rule_products_domain':"[]",
            'rule_minimum_amount_tax_inclusion':'tax_excluded',
        })

        #Case1:priceunit=5,qty=2,total=10,noreward
        order=self.empty_order
        order.write({
            'order_line':[(0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':2.0,
            })]
        })
        order.recompute_coupon_lines()
        msg="""
            Thepromoshouldn'thavebeenappliedastheorderamountisnotenoughafter
            applyingpromowithfreeproduct.
        """
        self.assertEqual(len(order.order_line.ids),1,msg)
        self.assertEqual(order.amount_untaxed,10)

        #Case2:priceunit=5,qty=5,total=25-5,1reward(5)
        order=self.env['sale.order'].create({'partner_id':self.steve.id})
        order.write({
            'order_line':[(0,False,{
                'product_id':self.product_B.id,
                'name':'5ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':5.0,
                })]
        })
        order.recompute_coupon_lines()
        promo_lines=order.order_line.filtered(lambdal:l.is_reward_line)
        msg="Thepromooffershouldhavebeenappliedonlyonce."
        self.assertEqual(len(promo_lines),1,msg)
        self.assertEqual(promo_lines[0].product_uom_qty,1,msg)
        self.assertEqual(order.amount_untaxed,20)

        #Case3:priceunit=5,qty=6,total=30-10,2rewards(2*5)
        order=self.env['sale.order'].create({'partner_id':self.steve.id})
        order.write({
            'order_line':[(0,False,{
                'product_id':self.product_B.id,
                'name':'6ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':6.0,
                })]
        })
        order.recompute_coupon_lines()
        promo_lines=order.order_line.filtered(lambdal:l.is_reward_line)
        msg="Thepromooffershouldhavebeenappliedtwice."
        self.assertEqual(len(promo_lines),1,msg)
        self.assertEqual(promo_lines[0].product_uom_qty,2,msg)
        self.assertEqual(order.amount_untaxed,20)

    deftest_program_rules_validity_dates_and_uses(self):
        #Testcase:Basedonthevaliditydatesandthenumberofalloweduses

        self.immediate_promotion_program.write({
            'rule_date_from':Date.to_string((datetime.now()-timedelta(days=7))),
            'rule_date_to':Date.to_string((datetime.now()-timedelta(days=2))),
            'maximum_use_number':1,
        })

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
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedwe'renotbetweenthevaliditydates")

        self.immediate_promotion_program.write({
            'rule_date_from':Date.to_string((datetime.now()-timedelta(days=7))),
            'rule_date_to':Date.to_string((datetime.now()+timedelta(days=2))),
        })
        order=self.env['sale.order'].create({'partner_id':self.steve.id})
        order.write({'order_line':[
            (0,False,{
                'product_id':self.product_A.id,
                'name':'1ProductA',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':10.0,
            }),
            (0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffertshouldhavebeenappliedaswe'rebetweenthevaliditydates")
        order=self.env['sale.order'].create({'partner_id':self.env['res.partner'].create({'name':'MyPartner'}).id})
        order.write({'order_line':[
            (0,False,{
                'product_id':self.product_A.id,
                'name':'1ProductA',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':10.0,
            }),
            (0,False,{
                'product_id':self.product_B.id,
                'name':'2ProductB',
                'product_uom':self.uom_unit.id,
                'product_uom_qty':1.0,
            })
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedasthenumberofusesisexceeded")

    deftest_program_rules_one_date(self):
        #Testcase:Basedonthevaliditydatesandthenumberofalloweduses

        #VFENOTEthe.rule_idisnecessarytoensurethedatesconstraintsdoesn'traise
        #becausetheormappliestherelatedinverseonebyone,raisingtheconstraint...
        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':False,
            'rule_date_to':Date.to_string((datetime.now()-timedelta(days=2))),
        })

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
        self.assertNotIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedwe'renotbetweenthevaliditydates")

        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':Date.to_string((datetime.now()+timedelta(days=1))),
            'rule_date_to':False,
        })
        order.recompute_coupon_lines()
        self.assertNotIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedwe'renotbetweenthevaliditydates")

        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':False,
            'rule_date_to':Date.to_string((datetime.now()+timedelta(days=2))),
        })
        order.recompute_coupon_lines()
        self.assertIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffershouldhavebeenappliedaswe'rebetweenthevaliditydates")

        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':Date.to_string((datetime.now()-timedelta(days=1))),
            'rule_date_to':False,
        })
        order.recompute_coupon_lines()
        self.assertIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffershouldhavebeenappliedaswe'rebetweenthevaliditydates")

    deftest_program_rules_date(self):
        #Testcase:Basedonthevaliditydates

        #VFENOTEthe.rule_idisnecessarytoensurethedatesconstraintsdoesn'traise
        #becausetheormappliestherelatedinverseonebyone,raisingtheconstraint...
        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':Date.to_string((datetime.now()-timedelta(days=7))),
            'rule_date_to':Date.to_string((datetime.now()-timedelta(days=2))),
        })

        order=self.empty_order
        order.write({
            'date_order':Date.to_string((datetime.now()-timedelta(days=5))),
        })
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
        self.assertNotIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedwe'renotbetweenthevaliditydates")

        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':Date.to_string((datetime.now()+timedelta(days=2))),
            'rule_date_to':Date.to_string((datetime.now()+timedelta(days=7))),
        })
        order.recompute_coupon_lines()
        self.assertNotIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),2,"Thepromooffertshouldn'thavebeenappliedwe'renotbetweenthevaliditydates")

        self.immediate_promotion_program.rule_id.write({
            'rule_date_from':Date.to_string((datetime.now()-timedelta(days=2))),
            'rule_date_to':Date.to_string((datetime.now()+timedelta(days=2))),
        })
        order.recompute_coupon_lines()
        self.assertIn(self.immediate_promotion_program,order._get_applicable_programs())
        self.assertEqual(len(order.order_line.ids),3,"Thepromooffershouldhavebeenappliedaswe'rebetweenthevaliditydates")

    deftest_program_rules_coupon_qty_and_amount_remove_not_eligible(self):
        '''Thistestwill:
                *Checkquantityandamountrequirementsworksasexpected(sinceit'sslightlydifferentfromapromotion_program)
                *Ensurethatifarewardfromacoupon_programwasallowedandtheconditionsarenotmetanymore,
                  therewardwillberemovedonrecompute.
        '''
        self.immediate_promotion_program.active=False #Avoidhavingthisprogramtoaddrewardsonthistest
        order=self.empty_order

        program=self.env['coupon.program'].create({
            'name':'Get10%discountifbuyatleast4ProductAand$320',
            'program_type':'coupon_program',
            'reward_type':'discount',
            'discount_type':'percentage',
            'discount_percentage':10.0,
            'rule_products_domain':"[('id','in',[%s])]"%(self.product_A.id),
            'rule_min_quantity':3,
            'rule_minimum_amount':320.00,
        })

        sol1=self.env['sale.order.line'].create({
            'product_id':self.product_A.id,
            'name':'ProductA',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        sol2=self.env['sale.order.line'].create({
            'product_id':self.product_B.id,
            'name':'ProductB',
            'product_uom_qty':4.0,
            'order_id':order.id,
        })

        #Defaultvalueforcoupongeneratewizardisgeneratebyquantityandgenerateonlyonecoupon
        self.env['coupon.generate.wizard'].with_context(active_id=program.id).create({}).generate_coupon()
        coupon=program.coupon_ids[0]

        #Notenoughamountsinceweonlyhave220(100*2+5*4)
        withself.assertRaises(UserError):
            self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':coupon.code
            }).process_coupon()

        sol2.product_uom_qty=24

        #Notenoughqtysinceweonlyhave3ProductA(Amountisok:100*2+5*24=320)
        withself.assertRaises(UserError):
            self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':coupon.code
            }).process_coupon()

        sol1.product_uom_qty=3

        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line.ids),3,"TheordershouldcontainstheProductAline,theProductBlineandthediscountline")
        self.assertEqual(coupon.state,'used',"ThecouponshouldbesettoConsumedasithasbeenused")

        sol1.product_uom_qty=2
        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line.ids),2,"Thediscountlineshouldhavebeenremovedaswedon'tmeettheprogramrequirements")
        self.assertEqual(coupon.state,'new',"ThecouponshouldberesettoValidasit'srewardgotremoved")


    deftest_program_rules_promotion_use_best(self):
        '''Thistestwill:
                *Verifythebestglobalpromotionaccordingtothe
                  currentsaleorderisused.
        '''
        self.immediate_promotion_program.active=False #Avoidhavingthisprogramtoaddrewardsonthistest
        order=self.empty_order

        program_5pc=self.env['coupon.program'].create({
            'name':'Get5%discountifbuyatleast2Product',
            'program_type':'promotion_program',
            'reward_type':'discount',
            'discount_type':'percentage',
            'discount_percentage':5.0,
            'rule_min_quantity':2,
            'promo_code_usage':'no_code_needed',
        })
        program_10pc=self.env['coupon.program'].create({
            'name':'Get10%discountifbuyatleast4Product',
            'program_type':'promotion_program',
            'reward_type':'discount',
            'discount_type':'percentage',
            'discount_percentage':10.0,
            'rule_min_quantity':4,
            'promo_code_usage':'no_code_needed',
        })
        sol=self.env['sale.order.line'].create({
            'product_id':self.product_A.id,
            'name':'ProductA',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"TheordershouldonlycontainstheProductAline")

        sol.product_uom_qty=3
        order.recompute_coupon_lines()
        discounts=set(order.order_line.mapped('name'))-{'ProductA'}
        self.assertEqual(len(discounts),1,"TheordershouldcontainstheProductAlineandadiscount")
        #Thenameofthediscountisdynamicallychangedtosmthlookinglike:
        #"Discount:Get5%discountifbuyatleast2Product-Onproductwithfollowingtax:Tax15.00%"
        self.assertTrue('Get5%discount'indiscounts.pop(),"Thediscountshouldbea5%discount")

        sol.product_uom_qty=5
        order.recompute_coupon_lines()
        discounts=set(order.order_line.mapped('name'))-{'ProductA'}
        self.assertEqual(len(discounts),1,"TheordershouldcontainstheProductAlineandadiscount")
        self.assertTrue('Get10%discount'indiscounts.pop(),"Thediscountshouldbea10%discount")
