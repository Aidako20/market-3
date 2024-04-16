#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale_coupon.tests.commonimportTestSaleCouponCommon
fromflectra.exceptionsimportUserError
fromflectra.testsimporttagged
fromflectra.tools.float_utilsimportfloat_compare


@tagged('post_install','-at_install')
classTestSaleCouponProgramNumbers(TestSaleCouponCommon):

    defsetUp(self):
        super(TestSaleCouponProgramNumbers,self).setUp()

        self.largeCabinet=self.env['product.product'].create({
            'name':'LargeCabinet',
            'list_price':320.0,
            'taxes_id':False,
        })
        self.conferenceChair=self.env['product.product'].create({
            'name':'ConferenceChair',
            'list_price':16.5,
            'taxes_id':False,
        })
        self.pedalBin=self.env['product.product'].create({
            'name':'PedalBin',
            'list_price':47.0,
            'taxes_id':False,
        })
        self.drawerBlack=self.env['product.product'].create({
            'name':'DrawerBlack',
            'list_price':25.0,
            'taxes_id':False,
        })
        self.largeMeetingTable=self.env['product.product'].create({
            'name':'LargeMeetingTable',
            'list_price':40000.0,
            'taxes_id':False,
        })

        self.steve=self.env['res.partner'].create({
            'name':'SteveBucknor',
            'email':'steve.bucknor@example.com',
        })
        self.empty_order=self.env['sale.order'].create({
            'partner_id':self.steve.id
        })

        self.p1=self.env['coupon.program'].create({
            'name':'Codefor10%onorders',
            'promo_code_usage':'code_needed',
            'promo_code':'test_10pc',
            'discount_type':'percentage',
            'discount_percentage':10.0,
            'program_type':'promotion_program',
        })
        self.p2=self.env['coupon.program'].create({
            'name':'Buy3cabinets,getoneforfree',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':self.largeCabinet.id,
            'rule_min_quantity':3,
            'rule_products_domain':'[["name","ilike","largecabinet"]]',
        })
        self.p3=self.env['coupon.program'].create({
            'name':'Buy1drawerblack,getafreeLargeMeetingTable',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':self.largeMeetingTable.id,
            'rule_products_domain':'[["name","ilike","drawerblack"]]',
        })
        self.discount_coupon_program=self.env['coupon.program'].create({
            'name':'$100coupon',
            'program_type':'coupon_program',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':100,
            'active':True,
            'discount_apply_on':'on_order',
            'rule_minimum_amount':100.00,
        })

    deftest_program_numbers_free_and_paid_product_qty(self):
        #Thesetestswillfocusonnumbers(freeproductqty,SOtotal,reductiontotal..)
        order=self.empty_order
        sol1=self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':4.0,
            'order_id':order.id,
        })

        #Checkwecorrectlygetafreeproduct
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Weshouldhave2linesaswenowhaveone'FreeLargeCabinet'lineaswebought4ofthem")

        #Checkfreeproduct'spriceisnotaddedtototalwhenapplyingreduction(Orthediscountwillalsobeappliedonthefreeproduct'sprice)
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'test_10pc')
        self.assertEqual(len(order.order_line.ids),3,"Weshould3linesasweshouldhaveanewlineforpromocodereduction")
        self.assertEqual(order.amount_total,864,"Onlypaidproductshouldhavetheirpricediscounted")
        order.order_line.filtered(lambdax:'Discount'inx.name).unlink() #RemoveDiscount

        #Checkfreeproductisremovedsincewearebelowminimumrequiredquantity
        sol1.product_uom_qty=3
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"FreeLargeCabinetshouldhavebeenremoved")

        #Freeproductincartwillbeconsideredaspaidproductwhenchangingquantityofpaidproduct,sothefreeproductquantitycomputationwillbewrong.
        #100LargeCabinetincart,25free,setquantityto10LargeCabinet,youshouldhave2freeLargeCabinetbutyouget8becauseitaddthe25initialfreeLargeCabinettothetotalpaidLargeCabinetwhencomputing(25+10>35>/4=8freeLargeCabinet)
        sol1.product_uom_qty=100
        order.recompute_coupon_lines()
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).product_uom_qty,25,"Weshouldhave25FreeLargeCabinet")
        sol1.product_uom_qty=10
        order.recompute_coupon_lines()
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).product_uom_qty,2,"Weshouldhave2FreeLargeCabinet")

    deftest_program_numbers_check_eligibility(self):
        #Thesetestswillfocusonnumbers(freeproductqty,SOtotal,reductiontotal..)

        #Checkifwehaveenoughpaidproducttoreceivefreeproductincaseofafreeproductthatisdifferentfromthepaidproductrequired
        #BuyA,getfreeb.(rememberweneedapaidBincarttoreceivefreeb).Ifyourcartis4A1Bthenyoushouldreceive1b(youareeligibletoreceive4becauseyouhave4AbutsinceyoudonthaveenoughtBinyourcart,youarelimitedtotheBquantity)
        order=self.empty_order
        sol1=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'drawerblack',
            'product_uom_qty':4.0,
            'order_id':order.id,
        })
        sol2=self.env['sale.order.line'].create({
            'product_id':self.largeMeetingTable.id,
            'name':'LargeMeetingTable',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"Weshouldhavea'FreeLargeMeetingTable'promotionline")
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).product_uom_qty,1,"WeshouldreceiveoneandonlyonefreeLargeMeetingTable")

        #Checktherequiredvalueamounttobeeligiblefortheprogramiscorrectlycomputed(eg:itdoesnotaddnegativevalue(fromfreeproduct)tototal)
        #A=freeb|HaveyourcartwithA2Bb|cartvalueshouldbeA+1BbutincodeitisonlyA(freebvalueissubsstract2times)
        #Thisisbecause_amount_all()issummingallSOlines(so+(-b.value))andagainin_check_promo_code()order.amount_untaxed+order.reward_amount|amount_untaxedhasalreadyfreeproductvaluesubstracted(_amount_all)
        sol1.product_uom_qty=1
        sol2.product_uom_qty=2
        self.p1.rule_minimum_amount=5000
        order.recompute_coupon_lines()
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'test_10pc')
        self.assertEqual(len(order.order_line.ids),4,"Weshouldhave4linesasweshouldhaveanewlineforpromocodereduction")

        #Checkyoucanstillhaveautoappliedpromotionifyouhaveapromocodesettotheorder
        self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':4.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),6,"Weshouldhave2morelinesaswenowhaveone'FreeLargeCabinet'linesincewebought4ofthem")

    deftest_program_numbers_taxes_and_rules(self):
        percent_tax=self.env['account.tax'].create({
            'name':"15%Tax",
            'amount_type':'percent',
            'amount':15,
            'price_include':True,
        })
        p_specific_product=self.env['coupon.program'].create({
            'name':'20%reductiononLargeCabinetincart',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':20.0,
            'rule_minimum_amount':320.00,
            'discount_apply_on':'specific_products',
            'discount_specific_product_ids':[(6,0,[self.largeCabinet.id])],
        })
        order=self.empty_order
        self.largeCabinet.taxes_id=percent_tax
        sol1=self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Weshouldnotgetthereductionlinesincewedonthave320$taxexcluded(cabinetis320$taxincluded)")
        sol1.tax_id.price_include=False
        sol1._compute_tax_id()
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Weshouldnowgetthereductionlinesincewehave320$taxincluded(cabinetis320$taxincluded)")
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair    | 1 |   320.00 |15%excl| 320.00| 368.00|  48.00
        #20%discounton     | 1 |   -64.00 |15%excl| -64.00| -73.60|  -9.60
        #       largecabinet|
        #--------------------------------------------------------------------------------
        #TOTAL                                             | 256.00| 294.40|  38.40
        self.assertAlmostEqual(order.amount_total,294.4,2,"Checkdiscounthasbeenappliedcorrectly(eg:ontaxesaswell)")

        #testcouponwithcodeworksthesameasautoapplied_programs
        p_specific_product.write({'promo_code_usage':'code_needed','promo_code':'20pc'})
        order.order_line.filtered(lambdal:l.is_reward_line).unlink()
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Reductionshouldberemovedsincewedeleteditanditisnowapromocodeusage,itshouldn'tbeautomaticallyreapplied")

        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'20pc')
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Weshouldnowgetthereductionlinesincewehave320$taxincluded(cabinetis320$taxincluded)")

        #checkdiscountappliedonlyonLargeCabinet
        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'DrawerBlack',
            'product_uom_qty':10.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #DrawerBlack        |10 |    25.00 |       /| 250.00| 250.00|      /
        #LargeCabinet       | 1 |   320.00 |15%excl| 320.00| 368.00|  48.00
        #20%discounton     | 1 |   -64.00 |15%excl| -64.00| -73.60|  -9.60
        #       largecabinet|
        #--------------------------------------------------------------------------------
        #TOTAL                                             | 506.00| 544.40|  38.40
        self.assertEqual(order.amount_total,544.4,"Weshouldonlygetreductiononcabinet")
        sol1.product_uom_qty=10
        order.recompute_coupon_lines()
        #Note:Sincewenowhave2freeLargeCabinet,weshoulddiscountonly8ofthe10LargeCabinetincartssincewedon'twanttodiscountfreeLargeCabinet
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #DrawerBlack        |10 |    25.00 |       /| 250.00| 250.00|      /
        #LargeCabinet       |10 |   320.00 |15%excl|3200.00|3680.00| 480.00
        #FreeLargeCabinet  | 2 |  -320.00 |15%excl|-640.00|-736.00| -96.00
        #20%discounton     | 1 |  -512.00 |15%excl|-512.00|-588.80| -78.80
        #       largecabinet|
        #--------------------------------------------------------------------------------
        #TOTAL                                             |2298.00|2605.20| 305.20
        self.assertAlmostEqual(order.amount_total,2605.20,2,"Changingcabinetquantityshouldchangediscountamountcorrectly")

        p_specific_product.discount_max_amount=200
        order.recompute_coupon_lines()
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #DrawerBlack        |10 |    25.00 |       /| 250.00| 250.00|      /
        #LargeCabinet       |10 |   320.00 |15%excl|3200.00|3680.00| 480.00
        #FreeLargeCabinet  | 2 |  -320.00 |15%excl|-640.00|-736.00| -96.00
        #20%discounton     | 1 |  -200.00 |15%excl|-200.00|-230.00| -30.00
        #       largecabinet|
        # limitedto200HTVA
        #--------------------------------------------------------------------------------
        #TOTAL                                             |2610.00|2964.00| 354.00
        self.assertEqual(order.amount_total,2964,"Thediscountshouldbelimitedto$200taxexcluded")
        self.assertEqual(order.amount_untaxed,2610,"Thediscountshouldbelimitedto$200taxexcluded(2)")

    deftest_program_numbers_one_discount_line_per_tax(self):
        order=self.empty_order
        #Createtaxes
        self.tax_15pc_excl=self.env['account.tax'].create({
            'name':"15%Taxexcl",
            'amount_type':'percent',
            'amount':15,
        })
        self.tax_50pc_excl=self.env['account.tax'].create({
            'name':"50%Taxexcl",
            'amount_type':'percent',
            'amount':50,
        })
        self.tax_35pc_incl=self.env['account.tax'].create({
            'name':"35%Taxincl",
            'amount_type':'percent',
            'amount':35,
            'price_include':True,
        })

        #Settaxandpricesonproductsasneeedforthetest
        (self.product_A+self.largeCabinet+self.conferenceChair+self.pedalBin+self.drawerBlack).write({'list_price':100})
        (self.largeCabinet+self.drawerBlack).write({'taxes_id':[(4,self.tax_15pc_excl.id,False)]})
        self.conferenceChair.taxes_id=self.tax_10pc_incl
        self.pedalBin.taxes_id=None
        self.product_A.taxes_id=(self.tax_35pc_incl+self.tax_50pc_excl)

        #Addproductsinorder
        self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':7.0,
            'order_id':order.id,
        })
        sol2=self.env['sale.order.line'].create({
            'product_id':self.conferenceChair.id,
            'name':'ConferenceChair',
            'product_uom_qty':5.0,
            'order_id':order.id,
        })
        self.env['sale.order.line'].create({
            'product_id':self.pedalBin.id,
            'name':'PedalBin',
            'product_uom_qty':10.0,
            'order_id':order.id,
        })
        self.env['sale.order.line'].create({
            'product_id':self.product_A.id,
            'name':'productAwithmultipletaxes',
            'product_uom_qty':3.0,
            'order_id':order.id,
        })
        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'DrawerBlack',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        #Createneededprograms
        self.p2.active=False
        self.p_large_cabinet=self.env['coupon.program'].create({
            'name':'Buy1largecabinet,getoneforfree',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':self.largeCabinet.id,
            'rule_products_domain':'[["name","ilike","largecabinet"]]',
        })
        self.p_conference_chair=self.env['coupon.program'].create({
            'name':'Buy1chair,getoneforfree',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':self.conferenceChair.id,
            'rule_products_domain':'[["name","ilike","conferencechair"]]',
        })
        self.p_pedal_bin=self.env['coupon.program'].create({
            'name':'Buy1bin,getoneforfree',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':self.pedalBin.id,
            'rule_products_domain':'[["name","ilike","pedalbin"]]',
        })

        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair    | 5 |   100.00 |10%incl| 454.55| 500.00|  45.45
        #Pedalbin           | 10|   100.00 |/       |1000.00|1000.00|      /
        #LargeCabinet       | 7 |   100.00 |15%excl| 700.00| 805.00| 105.00
        #DrawerBlack        | 2 |   100.00 |15%excl| 200.00| 230.00|  30.00
        #ProductA           | 3 |   100.00 |35%incl| 222.22| 411.11| 188.89
        #                                          50%excl
        #--------------------------------------------------------------------------------
        #TOTAL                                             |2576.77|2946.11| 369.34

        self.assertEqual(order.amount_total,2946.11,"Theordertotalwithoutanyprogramsshouldbe2946.11")
        self.assertEqual(order.amount_untaxed,2576.77,"Theorderuntaxedtotalwithoutanyprogramsshouldbe2576.77")
        self.assertEqual(len(order.order_line.ids),5,"Theorderwithoutanyprogramsshouldhave5lines")

        #Applyalltheprograms
        order.recompute_coupon_lines()

        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #FreeConferenceChair| 2 |  -100.00 |10%incl|-181.82|-200.00| -18.18
        #FreePedalBin      | 5 |  -100.00 |/       |-500.00|-500.00|      /
        #FreeLargeCabinet  | 3 |  -100.00 |15%excl|-300.00|-345.00| -45.00
        #--------------------------------------------------------------------------------
        #TOTALAFTERAPPLYINGFREEPRODUCTPROGRAMS        |1594.95|1901.11| 306.16

        self.assertAlmostEqual(order.amount_total,1901.11,2,"Theordertotalwithprogramsshouldbe1901.11")
        self.assertEqual(order.amount_untaxed,1594.95,"Theorderuntaxedtotalwithprogramsshouldbe1594.95")
        self.assertEqual(len(order.order_line.ids),8,"Ordershouldcontains5regularproductlinesand3freeproductlines")

        #Apply10%ontopofeverything
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'test_10pc')

        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #10%ontax10%incl | 1 |   -30.00 |10%incl|-27.27 |-30.00 |  -2.73
        #10%onnotax       | 1 |   -50.00 |/       |-50.00 |-50.00 |      /
        #10%ontax15%excl | 1 |   -40.00 |15%excl|-60.00 |-69.00 |  -9.00
        #10%ontax35%+50%  | 1 |   -30.00 |35%incl|-22.22 |-45.00 | -18.89
        #                                          50%excl
        #--------------------------------------------------------------------------------
        #TOTALAFTERAPPLYING10%GLOBALPROGRAM           |1435.46|1711.00|275.54

        self.assertEqual(order.amount_total,1711,"Theordertotalwithprogramsshouldbe1711")
        self.assertEqual(order.amount_untaxed,1435.46,"Theorderuntaxedtotalwithprogramsshouldbe1435.46")
        self.assertEqual(len(order.order_line.ids),12,"Ordershouldcontains5regularproductlines,3freeproductlinesand4discountlines(oneforeverytax)")

        #--Thisisatestinsidethetest
        order.order_line._compute_tax_id()
        self.assertEqual(order.amount_total,1711,"Recomputingtaxonsaleorderlinesshouldnotchangetotalamount")
        self.assertEqual(order.amount_untaxed,1435.46,"Recomputingtaxonsaleorderlinesshouldnotchangeuntaxedamount")
        self.assertEqual(len(order.order_line.ids),12,"Recomputingtaxonsaleorderlinesshouldnotchangenumberoforderline")
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,1711,"Recomputingtaxonsaleorderlinesshouldnotchangetotalamount")
        self.assertEqual(order.amount_untaxed,1435.46,"Recomputingtaxonsaleorderlinesshouldnotchangeuntaxedamount")
        self.assertEqual(len(order.order_line.ids),12,"Recomputingtaxonsaleorderlinesshouldnotchangenumberoforderline")
        #--Endtestinsidethetest

        #Nowwewanttoapplya20%discountonlyonLargeCabinet
        self.env['coupon.program'].create({
            'name':'20%reductiononLargeCabinetincart',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':20.0,
            'discount_apply_on':'specific_products',
            'discount_specific_product_ids':[(6,0,[self.largeCabinet.id])],
        })
        order.recompute_coupon_lines()
        #Note:wehave7regularLargeCabinetsand3freeLargeCabinets.Weshouldthendiscountonly4reallypaidLargeCabinets

        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #20%onLargeCabinet| 1 |   -80.00 |15%excl|-80.00 |-92.00 | -12.00
        #--------------------------------------------------------------------------------
        #TOTALAFTERAPPLYING20%ONLARGECABINET         |1355.45|1619.00|263.54

        self.assertEqual(order.amount_total,1619,"Theordertotalwithprogramsshouldbe1619")
        self.assertEqual(order.amount_untaxed,1355.46,"Theorderuntaxedtotalwithprogramsshouldbe1435.45")
        self.assertEqual(len(order.order_line.ids),13,"Ordershouldhaveanewdiscountlinefor20%onLargeCabinet")

        #Checkthatifyoudeleteoneofthediscounttaxline,theotherstaxlinesfromthesamepromotiongotdeletedaswell.
        order.order_line.filtered(lambdal:'10%'inl.name)[0].unlink()
        self.assertEqual(len(order.order_line.ids),9,"Allofthe10%discountlinepertaxshouldberemoved")
        #Atthispoint,removingtheConferenceChair'sdiscountline(splitpertax)removedalsotheothersdiscountlines
        #linkedtothesameprogram(eg:othertaxeslines).SothecoupongotremovedfromtheSOsincetherewerenodiscountlinesleft

        #Addbackthecoupontocontinuethetestflow
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'test_10pc')
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),13,"The10%discountlineshouldbeback")

        #Checkthatifyouchangeaproductqty,hisdiscounttaxlinegotupdated
        sol2.product_uom_qty=7
        order.recompute_coupon_lines()
        #ConferenceChair    | 5 |   100.00 |10%incl| 454.55| 500.00|  45.45
        #FreeConferenceChair| 2 |  -100.00 |10%incl|-181.82|-200.00| -18.18
        #10%ontax10%incl | 1 |   -30.00 |10%incl|-27.27 |-30.00 |  -2.73
        #--------------------------------------------------------------------------------
        #TOTALOFConferenceChairLINES                               | 245.46| 270.00|  24.54
        #==>Shouldbecome:
        #ConferenceChair    | 7 |   100.00 |10%incl| 636.36| 700.00|  63.64
        #FreeConferenceChair| 3 |  -100.00 |10%incl|-272.73|-300.00| -27.27
        #10%ontax10%incl | 1 |   -40.00 |10%incl| -36.36| -40.00|  -3.64
        #--------------------------------------------------------------------------------
        #TOTALOFConferenceChairLINES                   | 327.27| 360.00|  32.73
        #AFTERADDING2ConferenceChair                   |
        #--------------------------------------------------------------------------------
        #=>DIFFERENCESBEFORE/AFTER                       |  81.81|  90.00|   8.19
        self.assertEqual(order.amount_untaxed,1355.46+81.81,"TheordershouldhaveonemorepaidConferenceChairwith10%incltaxanddiscountedby10%")

        #Checkthatifyouremoveaproduct,hisrewardlinesgotremoved,especiallythediscountpertaxone
        sol2.unlink()
        order.recompute_coupon_lines()
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #PedalBins          | 10|   100.00 |/       |1000.00|1000.00|      /
        #LargeCabinet       | 7 |   100.00 |15%excl| 700.00| 805.00| 105.00
        #DrawerBlack        | 2 |   100.00 |15%excl| 200.00| 230.00|  30.00
        #ProductA           | 3 |   100.00 |35%incl| 222.22| 411.11| 188.89
        #                                          50%excl
        #FreePedalBin      | 5 |  -100.00 |/       |-500.00|-500.00|      /
        #FreeLargeCabinet  | 3 |  -100.00 |15%excl|-300.00|-345.00| -45.00
        #20%onLargeCabinet| 1 |   -80.00 |15%excl|-80.00 |-92.00 | -12.00
        #10%onnotax       | 1 |   -50.00 |/       |-50.00 |-50.00 |      /
        #10%ontax15%excl | 1 |   -60.00 |15%excl|-60.00 |-69.00 |  -9.00
        #10%ontax35%+50%  | 1 |   -30.00 |35%incl|-22.22 |-41.11 | -18.89
        #                                          50%excl
        #--------------------------------------------------------------------------------
        #TOTAL                                             |1110.0 |1349.11|  239.0
        self.assertAlmostEqual(order.amount_total,1349.0,2,"Theordertotalwithprogramsshouldbe1509.11")
        self.assertEqual(order.amount_untaxed,1110.0,"Theorderuntaxedtotalwithprogramsshouldbe1242.22")
        self.assertEqual(len(order.order_line.ids),10,"Ordershouldcontains7lines:4productslines,"
                                                        "2freeproductslines,a20%discountline"
                                                        "and310%discount")

    deftest_program_numbers_extras(self):
        #Checkthatyoucan'tapplyaglobaldiscountpromocodeifthereisalreadyanautoappliedglobaldiscount
        self.p1.copy({'promo_code_usage':'no_code_needed','name':'Autoapplied10%globaldiscount'})
        order=self.empty_order
        self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Weshouldget1LargeCabinetlineand110%autoappliedglobaldiscountline")
        self.assertEqual(order.amount_total,288,"320$-10%")
        withself.assertRaises(UserError):
            #Can'tapplyasecondglobaldiscount
            self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':'test_10pc'
            }).process_coupon()

    deftest_program_fixed_price(self):
        #Checkfixedamountdiscount
        order=self.empty_order
        fixed_amount_program=self.env['coupon.program'].create({
            'name':'$249discount',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':249.0,
        })
        self.tax_0pc_excl=self.env['account.tax'].create({
            'name':"0%Taxexcl",
            'amount_type':'percent',
            'amount':0,
        })
        fixed_amount_program.discount_line_product_id.write({'taxes_id':[(4,self.tax_0pc_excl.id,False)]})
        sol1=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'DrawerBlack',
            'product_uom_qty':1.0,
            'order_id':order.id,
            'tax_id':[(4,self.tax_0pc_excl.id)]
        })
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,0,"Totalshouldbenull.ThefixedamountdiscountishigherthantheSOtotal,itshouldbereducedtotheSOtotal")
        self.assertEqual(len(order.order_line.ids),2,"Thereshouldbetheproductlineandtherewardline")
        sol1.product_uom_qty=17
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,176,"Fixedamountdiscountshouldbetotallydeduced")
        self.assertEqual(len(order.order_line.ids),2,"Numberoflinesshouldbeunchangedaswejustrecomputetherewardline")
        sol2=order.order_line.filtered(lambdal:l.id!=sol1.id)
        self.assertEqual(len(sol2.tax_id.ids),1,"Onetaxshouldbepresentontherewardline")
        self.assertEqual(sol2.tax_id.id,self.tax_0pc_excl.id,"Thetaxshouldbe0%Taxexcl")
        fixed_amount_program.write({'active':False}) #Checkarchivedproductwillremovediscountlinesonrecompute
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Archivingtheprogramshouldremovetheprogramrewardline")

    deftest_program_next_order(self):
        order=self.empty_order
        self.env['coupon.program'].create({
            'name':'FreePedalBinifatleast1article',
            'promo_code_usage':'no_code_needed',
            'promo_applicability':'on_next_order',
            'program_type':'promotion_program',
            'reward_type':'product',
            'reward_product_id':self.pedalBin.id,
            'rule_min_quantity':2,
        })
        sol1=self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Nothingshouldbeaddedtothecart")
        self.assertEqual(len(order.generated_coupon_ids),0,"Nocouponshouldhavebeengeneratedyet")

        sol1.product_uom_qty=2
        order.recompute_coupon_lines()
        generated_coupon=order.generated_coupon_ids
        self.assertEqual(len(order.order_line.ids),1,"Nothingshouldbeaddedtothecart(2)")
        self.assertEqual(len(generated_coupon),1,"Acouponshouldhavebeengenerated")
        self.assertEqual(generated_coupon.state,'reserved',"Thecouponshouldbereserved")

        sol1.product_uom_qty=1
        order.recompute_coupon_lines()
        generated_coupon=order.generated_coupon_ids
        self.assertEqual(len(order.order_line.ids),1,"Nothingshouldbeaddedtothecart(3)")
        self.assertEqual(len(generated_coupon),1,"Nomorecouponshouldhavebeengeneratedandtheexistingoneshouldnothavebeendeleted")
        self.assertEqual(generated_coupon.state,'expired',"Thecouponshouldhavebeensetasexpiredasitisnomorevalidsincewedon'thavetherequiredquantity")

        sol1.product_uom_qty=2
        order.recompute_coupon_lines()
        generated_coupon=order.generated_coupon_ids
        self.assertEqual(len(generated_coupon),1,"Weshouldstillhaveonly1couponaswenowbenefitagainfromtheprogrambutnoneedtocreateanewone(seenextassert)")
        self.assertEqual(generated_coupon.state,'reserved',"Thecouponshouldbesetbacktoreservedaswehadalreadyanexpiredone,noneedtocreateanewone")

    deftest_coupon_rule_minimum_amount(self):
        """Ensurecouponwithminimumamountrulearecorrectly
            appliedonorders
        """
        order=self.empty_order
        self.env['sale.order.line'].create({
            'product_id':self.conferenceChair.id,
            'name':'ConferenceChair',
            'product_uom_qty':10.0,
            'order_id':order.id,
        })
        self.assertEqual(order.amount_total,165.0,"Theorderamountisnotcorrect")
        self.env['coupon.generate.wizard'].with_context(active_id=self.discount_coupon_program.id).create({}).generate_coupon()
        coupon=self.discount_coupon_program.coupon_ids[0]
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        self.assertEqual(order.amount_total,65.0,"Thecouponshouldbecorrectlyapplied")
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,65.0,"Thecouponshouldnotberemovedfromtheorder")

    deftest_coupon_and_program_discount_fixed_amount(self):
        """Ensurecouponandprogramdiscountbothwith
            minimumamountrulecancohexistswithoutmaking
            theordergobelow0
        """
        order=self.empty_order
        orderline=self.env['sale.order.line'].create({
            'product_id':self.conferenceChair.id,
            'name':'ConferenceChair',
            'product_uom_qty':10.0,
            'order_id':order.id,
        })
        self.assertEqual(order.amount_total,165.0,"Theorderamountisnotcorrect")

        self.env['coupon.program'].create({
            'name':'$100promotionprogram',
            'program_type':'promotion_program',
            'promo_code_usage':'code_needed',
            'promo_code':'testpromo',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':100,
            'active':True,
            'discount_apply_on':'on_order',
            'rule_minimum_amount':100.00,
        })

        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':'testpromo'
        }).process_coupon()
        self.assertEqual(order.amount_total,65.0,"Thepromotionprogramshouldbecorrectlyapplied")
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,65.0,"Thepromotionprogramshouldnotberemovedafterrecomputation")

        self.env['coupon.generate.wizard'].with_context(active_id=self.discount_coupon_program.id).create({}).generate_coupon()
        coupon=self.discount_coupon_program.coupon_ids[0]
        withself.assertRaises(UserError):
            self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':coupon.code
            }).process_coupon()
        orderline.write({'product_uom_qty':15})
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        self.assertEqual(order.amount_total,47.5,"Thepromotionprogramshouldnowbecorrectlyapplied")

        orderline.write({'product_uom_qty':5})
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,82.5,"Thepromotionprogramsshouldhavebeenremovedfromtheordertoavoidnegativeamount")

    deftest_coupon_and_coupon_discount_fixed_amount_tax_excl(self):
        """Ensuremultiplecouponcancohexistswithoutmaking
            theordergobelow0
            *Haveanorderof300(3lines:1taxexcl15%,2notax)
            *ApplyacouponAof10%discount,unconditioned
            *ApplyacouponBof288.5discount,unconditioned
            *Ordershouldnotgobelow0
            *Evenapplyingthecouponinreverseordershouldyieldsameresult
        """

        coupon_program=self.env['coupon.program'].create({
            'name':'$288.5coupon',
            'program_type':'coupon_program',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':288.5,
            'active':True,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order
        orderline=self.env['sale.order.line'].create([
        {
            'product_id':self.conferenceChair.id,
            'name':'ConferenceChair',
            'product_uom_qty':1.0,
            'price_unit':100.0,
            'order_id':order.id,
            'tax_id':[(6,0,(self.tax_15pc_excl.id,))],
        },
        {
            'product_id':self.pedalBin.id,
            'name':'ComputerCase',
            'product_uom_qty':1.0,
            'price_unit':100.0,
            'order_id':order.id,
            'tax_id':[(6,0,[])],
        },
        {
            'product_id':self.product_A.id,
            'name':'ComputerCase',
            'product_uom_qty':1.0,
            'price_unit':100.0,
            'order_id':order.id,
            'tax_id':[(6,0,[])],
        },
        ])

        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':'test_10pc'
            }).process_coupon()
        self.assertEqual(order.amount_total,283.5,"Thepromotionprogramshouldbecorrectlyapplied")

        self.env['coupon.generate.wizard'].with_context(active_id=coupon_program.id).create({
            'generation_type':'nbr_coupon',
            'nbr_coupons':1,
        }).generate_coupon()
        coupon=coupon_program.coupon_ids
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_tax,0)
        self.assertEqual(order.amount_untaxed,0.0,"Theuntaxedamountshouldnotgobelow0")
        self.assertEqual(order.amount_total,0,"Thepromotionprogramshouldnotmaketheordertotalgobelow0")

        order.order_line[3:].unlink()#removeallcoupon

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line),3,"Thepromotionprogramshouldberemoved")
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        self.assertEqual(order.amount_total,26.5,"Thepromotionprogramshouldbecorrectlyapplied")
        order.recompute_coupon_lines()
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':'test_10pc'
            }).process_coupon()
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_tax,0)
        self.assertEqual(order.amount_untaxed,0.0)
        self.assertEqual(order.amount_total,0,"Thepromotionprogramshouldnotmaketheordertotalgobelow0bealteredafterrecomputation")

    deftest_coupon_and_coupon_discount_fixed_amount_tax_incl(self):
        """Ensuremultiplecouponcancohexistswithoutmaking
            theordergobelow0
            *Haveanorderof300(3lines:1taxincl10%,2notax)
            *ApplyacouponAof10%discount,unconditioned
            *ApplyacouponBof290discount,unconditioned
            *Ordershouldnotgobelow0
            *Evenapplyingthecouponinreverseordershouldyieldsameresult
        """

        coupon_program=self.env['coupon.program'].create({
            'name':'$290coupon',
            'program_type':'coupon_program',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':290,
            'active':True,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order
        self.env['sale.order.line'].create([
        {
            'product_id':self.conferenceChair.id,
            'name':'ConferenceChair',
            'product_uom_qty':1.0,
            'price_unit':100.0,
            'order_id':order.id,
            'tax_id':[(6,0,(self.tax_10pc_incl.id,))],
        },
        {
            'product_id':self.pedalBin.id,
            'name':'ComputerCase',
            'product_uom_qty':1.0,
            'price_unit':100.0,
            'order_id':order.id,
            'tax_id':[(6,0,[])],
        },
        {
            'product_id':self.product_A.id,
            'name':'ComputerCase',
            'product_uom_qty':1.0,
            'price_unit':100.0,
            'order_id':order.id,
            'tax_id':[(6,0,[])],
        },
        ])

        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':'test_10pc'
            }).process_coupon()
        self.assertEqual(order.amount_total,270.0,"Thepromotionprogramshouldbecorrectlyapplied")

        self.env['coupon.generate.wizard'].with_context(active_id=coupon_program.id).create({
            'generation_type':'nbr_coupon',
            'nbr_coupons':1,
        }).generate_coupon()
        coupon=coupon_program.coupon_ids
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        self.assertEqual(order.amount_total,0.0,"Thepromotionprogramshouldnotmaketheordertotalgobelow0")
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,0.0,"Thepromotionprogramshouldnotbealteredafterrecomputation")

        order.order_line[3:].unlink()#removeallcoupon

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line),3,"Thepromotionprogramshouldberemoved")
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()
        self.assertEqual(order.amount_total,10.0,"Thepromotionprogramshouldbecorrectlyapplied")
        order.recompute_coupon_lines()
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
                'coupon_code':'test_10pc'
            }).process_coupon()
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,0.0,"Thepromotionprogramshouldnotbealteredafterrecomputation")

    deftest_program_percentage_discount_on_product_included_tax(self):
        #test100%percentagediscount(taxincluded)

        program=self.env['coupon.program'].create({
            'name':'100%discount',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_percentage':100.0,
            'rule_minimum_amount_tax_inclusion':'tax_included',
        })
        self.tax_10pc_incl.price_include=True

        self.drawerBlack.taxes_id=self.tax_10pc_incl
        order=self.empty_order
        order.order_line=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Thediscountshouldbeapplied")
        self.assertEqual(order.amount_total,0.0,"Ordershouldbe0asitisa100%discount")

        #test95%percentagediscount(taxincluded)
        program.discount_percentage=95
        order.recompute_coupon_lines()
        #lst_priceis25$sototalnowshouldbe1.25$(1.14$+0.11$taxes)
        self.assertEqual(len(order.order_line.ids),2,"Thediscountshouldbeapplied")
        self.assertAlmostEqual(order.amount_tax,0.11,places=2)
        self.assertAlmostEqual(order.amount_untaxed,1.14,places=2)

    deftest_program_discount_on_multiple_specific_products(self):
        """Ensureadiscountonmultiplespecificproductsiscorrectlycomputed.
            -Simple:Discountmustbeappliedonalltheproductssetonthepromotion
            -Advanced:Thisdiscountmustbesplitbydifferenttaxes
        """
        order=self.empty_order
        p_specific_products=self.env['coupon.program'].create({
            'name':'20%reductiononConferenceChairandDrawerBlackincart',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':25.0,
            'discount_apply_on':'specific_products',
            'discount_specific_product_ids':[(6,0,[self.conferenceChair.id,self.drawerBlack.id])],
        })

        self.env['sale.order.line'].create({
            'product_id':self.conferenceChair.id,
            'name':'ConferenceChair',
            'product_uom_qty':4.0,
            'order_id':order.id,
        })
        sol2=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'DrawerBlack',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"ConferenceChair+DrawerBlack+20%discountline")
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair    | 4 |    16.50 |      / |  66.00|  66.00|  0.00
        #DrawerBlack        | 2 |    25.00 |      / |  50.00|  50.00|  0.00
        #25%discount        | 1 |   -29.00 |      / | -29.00| -29.00|  0.00
        #--------------------------------------------------------------------------------
        #TOTAL                                             |  87.00|  87.00|  0.00
        self.assertEqual(order.amount_total,87.00,"Totalshouldbe87.00,seeabovecomment")

        #removeDrawerBlackcasefrompromotion
        p_specific_products.discount_specific_product_ids=[(6,0,[self.conferenceChair.id])]
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"ShouldstillbeConferenceChair+DrawerBlack+20%discountline")
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair    | 4 |    16.50 |      / |  66.00|  66.00|  0.00
        #DrawerBlack        | 2 |    25.00 |      / |  50.00|  50.00|  0.00
        #25%discount        | 1 |   -16.50 |      / | -16.50| -16.50|  0.00
        #--------------------------------------------------------------------------------
        #TOTAL                                             |  99.50|  99.50|  0.00
        self.assertEqual(order.amount_total,99.50,"The12.50discountfromthedrawerblackshouldbegone")

        #=========================================================================
        #PART2:SameflowbutwithdifferenttaxesonproductstoensurediscountissplitperVAT
        #AddbackDrawerBlackinpromotion
        p_specific_products.discount_specific_product_ids=[(6,0,[self.conferenceChair.id,self.drawerBlack.id])]

        percent_tax=self.env['account.tax'].create({
            'name':"30%Tax",
            'amount_type':'percent',
            'amount':30,
            'price_include':True,
        })
        sol2.tax_id=percent_tax

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),4,"ConferenceChair+DrawerBlack+20%onnoTVAproduct(ConferenceChair)+20%on15%tvaproduct(DrawerBlack)")
        #Name                |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair    | 4 |    16.50 |      / |  66.00|  66.00|  0.00
        #DrawerBlack        | 2 |    25.00 |30%incl|  38.46|  50.00| 11.54
        #25%discount        | 1 |   -16.50 |      / | -16.50| -16.50|  0.00
        #25%discount        | 1 |   -12.50 |30%incl|  -9.62| -12.50| -2.88
        #--------------------------------------------------------------------------------
        #TOTAL                                             |  78.34|  87.00|  8.66
        self.assertEqual(order.amount_total,87.00,"Totaluntaxedshouldbeasperabovecomment")
        self.assertEqual(order.amount_untaxed,78.34,"Totalwithtaxesshouldbeasperabovecomment")

    deftest_program_numbers_free_prod_with_min_amount_and_qty_on_same_prod(self):
        #Thistestfocusongivingafreeproductbasedonboth
        #minimumamountandquantityconditiononan
        #autoappliedpromotionprogram

        order=self.empty_order
        self.p3=self.env['coupon.program'].create({
            'name':'Buy2Chairs,get1free',
            'promo_code_usage':'no_code_needed',
            'reward_type':'product',
            'program_type':'promotion_program',
            'reward_product_id':self.conferenceChair.id,
            'rule_min_quantity':2,
            'rule_minimum_amount':self.conferenceChair.lst_price*2,
            'rule_products_domain':'[["sale_ok","=",True],["id","=",%d]]'%self.conferenceChair.id,
        })
        sol1=self.env['sale.order.line'].create({
            'product_id':self.conferenceChair.id,
            'name':'ConfChair',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })
        sol2=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'Drawer',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })#dummyline

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Thepromotionlinesshouldnotbeapplied")
        sol1.write({'product_uom_qty':3.0})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),3,"Thepromotionlinesshouldhavebeenadded")
        self.assertEqual(order.amount_total,self.conferenceChair.lst_price*(sol1.product_uom_qty-1)+self.drawerBlack.lst_price*sol2.product_uom_qty,"Thepromotionlinewasnotappliedtotheamounttotal")
        sol2.unlink()
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),2,"Theotherproductshouldnotaffectthepromotion")
        self.assertEqual(order.amount_total,self.conferenceChair.lst_price*(sol1.product_uom_qty-1),"Thepromotionlinewasnotappliedtotheamounttotal")
        sol1.write({'product_uom_qty':2.0})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids),1,"Thepromotionlinesshouldhavebeenremoved")

    deftest_program_step_percentages(self):
        #teststep-likepercentagesincreaseoveramount
        testprod=self.env['product.product'].create({
            'name':'testprod',
            'lst_price':118.0,
        })

        self.env['coupon.program'].create({
            'name':'10%discount',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':10.0,
            'rule_minimum_amount':1500.0,
            'rule_minimum_amount_tax_inclusion':'tax_included',
        })
        self.env['coupon.program'].create({
            'name':'15%discount',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':15.0,
            'rule_minimum_amount':1750.0,
            'rule_minimum_amount_tax_inclusion':'tax_included',
        })
        self.env['coupon.program'].create({
            'name':'20%discount',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':20.0,
            'rule_minimum_amount':2000.0,
            'rule_minimum_amount_tax_inclusion':'tax_included',
        })
        self.env['coupon.program'].create({
            'name':'25%discount',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':25.0,
            'rule_minimum_amount':2500.0,
            'rule_minimum_amount_tax_inclusion':'tax_included',
        })

        #apply10%
        order=self.empty_order
        order_line=self.env['sale.order.line'].create({
            'product_id':testprod.id,
            'name':'testprod',
            'product_uom_qty':14.0,
            'price_unit':118.0,
            'order_id':order.id,
            'tax_id':False,
        })
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,1486.80,"10%discountshouldbeapplied")
        self.assertEqual(len(order.order_line.ids),2,"discountshouldbeapplied")

        #switchto15%
        order_line.write({'product_uom_qty':15})
        self.assertEqual(order.amount_total,1604.8,"Discountimproperlyapplied")
        self.assertEqual(len(order.order_line.ids),2,"Nodiscountappliedwhileitshould")

        #switchto20%
        order_line.write({'product_uom_qty':17})
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,1604.8,"Discountimproperlyapplied")
        self.assertEqual(len(order.order_line.ids),2,"Nodiscountappliedwhileitshould")

        #still20%
        order_line.write({'product_uom_qty':20})
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,1888.0,"Discountimproperlyapplied")
        self.assertEqual(len(order.order_line.ids),2,"Nodiscountappliedwhileitshould")

        #backto10%
        order_line.write({'product_uom_qty':14})
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,1486.80,"Discountimproperlyapplied")
        self.assertEqual(len(order.order_line.ids),2,"Nodiscountappliedwhileitshould")

    deftest_program_free_prods_with_min_qty_and_reward_qty_and_rule(self):
        order=self.empty_order
        coupon_program=self.env['coupon.program'].create({
            'name':'2freeconferencechairifatleast1largecabinet',
            'promo_code_usage':'code_needed',
            'program_type':'promotion_program',
            'reward_type':'product',
            'reward_product_quantity':2,
            'reward_product_id':self.conferenceChair.id,
            'rule_min_quantity':1,
            'rule_products_domain':'["&",["sale_ok","=",True],["name","ilike","largecabinet"]]',
        })
        #setlargecabinetandconferencechairprices
        self.largeCabinet.write({'list_price':500,'sale_ok':True,})
        self.conferenceChair.write({'list_price':100,'sale_ok':True})

        #createSOL
        sol1=self.env['sale.order.line'].create({
            'product_id':self.largeCabinet.id,
            'name':'LargeCabinet',
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        sol2=self.env['sale.order.line'].create({
            'product_id':self.conferenceChair.id,
            'name':'Conferencechair',
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        self.assertEqual(len(order.order_line),2,'Theordermustcontain2orderlinessincethecouponisnotyetapplied')
        self.assertEqual(order.amount_total,700.0,'Thepricemustbe500.0sincethecouponisnotyetapplied')

        #generateandapplycoupon
        self.env['coupon.generate.wizard'].with_context(active_id=coupon_program.id).create({
            'generation_type':'nbr_coupon',
            'nbr_coupons':1,
        }).generate_coupon()
        coupon=coupon_program.coupon_ids
        self.env['sale.coupon.apply.code'].with_context(active_id=order.id).create({
            'coupon_code':coupon.code
        }).process_coupon()

        #Name                 |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair     | 2 |   100.00 |/       | 200.00| 200.00|      /
        #LargeCabinet        | 1 |   500.00 |/       | 500.00| 500.00|      /
        #
        #FreeConferenceChair| 2 |  -100.00 |/       |-200.00|-200.00|      /
        #--------------------------------------------------------------------------------
        #TOTAL                                              | 500.00| 500.00|      /

        self.assertEqual(len(order.order_line),3,'Theordermustcontain3orderlinesincludingoneforfreeconferencechair')
        self.assertEqual(order.amount_total,500.0,'Thepricemustbe500.0sincetwoconferencechairsarefree')
        self.assertEqual(order.order_line[2].price_total,-200.0,'Thelastorderlineshouldapplyareductionof200.0sincetherearetwoconferencechairsthatcost100.0each')

        #preventusertogetillicitediscountbydecreasingtheto1therewardproductqtyafterapplyingthecoupon
        sol2.product_uom_qty=1.0
        order.recompute_coupon_lines()

        #inthiscaseusershouldnothave-200.0
        #Name                 |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair     | 1 |   100.00 |/       | 100.00| 100.00|      /
        #LargeCabine         | 1 |   500.00 |/       | 500.00| 500.00|      /
        #
        #FreeConferenceChair| 2 |  -100.00 |/       |-200.00|-200.00|      /
        #--------------------------------------------------------------------------------
        #TOTAL                                              | 400.00| 400.00|      /


        #heshouldratherhavethisone
        #Name                 |Qty|price_unit| Tax    | HTVA  |  TVAC | TVA |
        #--------------------------------------------------------------------------------
        #ConferenceChair     | 1 |   100.00 |/       | 100.00| 100.00|      /
        #LargeCabinet        | 1 |   500.00 |/       | 500.00| 500.00|      /
        #
        #FreeConferenceChair| 1 |  -100.00 |/       |-100.00|-100.00|      /
        #--------------------------------------------------------------------------------
        #TOTAL                                              | 500.00| 500.00|      /

        self.assertEqual(order.amount_total,500.0,'Thepricemustbe500.0sincetwoconferencechairsarefreeandtheuseronlyboughtone')
        self.assertEqual(order.order_line[2].price_total,-100.0,'Thelastorderlineshouldapplyareductionof100.0sincethereisoneconferencechairthatcost100.0')

    deftest_program_free_product_different_than_rule_product_with_multiple_application(self):
        order=self.empty_order

        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'product_uom_qty':2.0,
            'order_id':order.id,
        })
        sol_B=self.env['sale.order.line'].create({
            'product_id':self.largeMeetingTable.id,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),3,'Theordermustcontain3orderlines:1xforBlackDrawer,1xforLargeMeetingTableand1xforfreeLargeMeetingTable')
        self.assertEqual(order.amount_total,self.drawerBlack.list_price*2,'Thepricemustbe50.0sincetheLargeMeetingTableisfree:2*25.00(BlackDrawer)+1*40000.00(LargeMeetingTable)-1*40000.00(freeLargeMeetingTable)')
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).product_uom_qty,1,"OnlyonefreeLargeMeetingTableshouldbeoffered,asonlyonepaidLargeMeetingTableisincart.Youcan'thavemorefreeproductthanpaidproduct.")

        sol_B.product_uom_qty=2

        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),3,'Theordermustcontain3orderlines:1xforBlackDrawer,1xforLargeMeetingTableand1xforfreeLargeMeetingTable')
        self.assertEqual(order.amount_total,self.drawerBlack.list_price*2,'Thepricemustbe50.0sincethe2LargeMeetingTablearefree:2*25.00(BlackDrawer)+2*40000.00(LargeMeetingTable)-2*40000.00(freeLargeMeetingTable)')
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).product_uom_qty,2,'The2LargeMeetingTableshouldbeoffered,asthepromotionsays1BlackDrawer=1freeLargeMeetingTableandthereare2BlackDrawer')

    deftest_program_modify_reward_line_qty(self):
        order=self.empty_order
        product_F=self.env['product.product'].create({
            'name':'ProductF',
            'list_price':100,
            'sale_ok':True,
            'taxes_id':[(6,0,[])],
        })
        self.env['coupon.program'].create({
            'name':'1ProductF=5$discount',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':5,
            'rule_products_domain':"[('id','in',[%s])]"%(product_F.id),
            'active':True,
        })

        self.env['sale.order.line'].create({
            'product_id':product_F.id,
            'product_uom_qty':2.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),2,'Theordermustcontain2orderlines:1xProductFand1x5$discount')
        self.assertEqual(order.amount_total,195.0,'Thepricemustbe195.0sincethereisa5$discountand2xProductF')
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).product_uom_qty,1,'Therewardlineshouldhaveaquantityof1sinceFixedAmountdiscountsapplyonlyonceperSaleOrder')

        order.order_line[1].product_uom_qty=2

        self.assertEqual(len(order.order_line),2,'Theordermustcontain2orderlines:1xProductFand1x5$discount')
        self.assertEqual(order.amount_total,190.0,'Thepricemustbe190.0sincethereisnow2x5$discountand2xProductF')
        self.assertEqual(order.order_line.filtered(lambdax:x.is_reward_line).price_unit,-5,'Thediscountunitpriceshouldstillbe-5afterthequantitywasmanuallychanged')

    deftest_program_maximum_use_number_with_other_promo(self):
        self.env['coupon.program'].create({
            'name':'20%discountonfirstorder',
            'promo_code_usage':'no_code_needed',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':20.0,
            'maximum_use_number':1,
        })
        self.p1.promo_code_usage='no_code_needed'

        #checkthat20%isappliedatfirstorder
        order=self.empty_order
        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,20.0,"20%discountshouldbeapplied")
        self.assertEqual(len(order.order_line.ids),2,"discountshouldbeapplied")

        #checkthat10%isappliedatsecondorder
        order2=self.env['sale.order'].create({'partner_id':self.steve.id})
        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'product_uom_qty':1.0,
            'order_id':order2.id,
        })
        order2.recompute_coupon_lines()
        self.assertEqual(order2.amount_total,22.5,"10%discountshouldbeapplied")
        self.assertEqual(len(order2.order_line.ids),2,"discountshouldbeapplied")

    deftest_program_maximum_use_number_last_order(self):
        #reusep1withadifferentpromocodeandamaximum_use_numberof1
        self.p1.promo_code='promo1'
        self.p1.maximum_use_number=1

        #checkthatthediscountisappliedonthefirstorder
        order=self.empty_order
        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'promo1')
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,22.5,"10%discountshouldbeapplied")
        self.assertEqual(len(order.order_line.ids),2,"discountshouldbeapplied")

        #duplicatingtomimicwebsitebehavior(eachrefreshto/shop/cart
        #recomputecouponlinesifwebsite_sale_couponisinstalled)
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,22.5,"10%discountshouldbeapplied")
        self.assertEqual(len(order.order_line.ids),2,"discountshouldbeapplied")
        #applyingthecodeagainshouldreturnthatithasbeenexpired.
        self.assertDictEqual(self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'promo1'),{'error':'Promocodepromo1hasbeenexpired.'})

    deftest_fixed_amount_taxes_attribution(self):

        self.env['coupon.program'].create({
            'name':'$5coupon',
            'program_type':'promotion_program',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':5,
            'active':True,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order
        sol=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()

        self.assertEqual(order.amount_total,5,'Priceshouldbe10$-5$(discount)=5$')
        self.assertEqual(order.amount_tax,0,'Notaxesareappliedyet')

        sol.tax_id=self.tax_10pc_base_incl
        order.recompute_coupon_lines()

        self.assertEqual(order.amount_total,5,'Priceshouldbe10$-5$(discount)=5$')
        self.assertEqual(float_compare(order.amount_tax,5/11,precision_rounding=3),0,'10%Taxincludedin5$')

        sol.tax_id=self.tax_10pc_excl
        order.recompute_coupon_lines()

        #Valueis5.99insteadof6becauseyoucannothave6with10%taxexcludedandaprecisionroundingof2
        self.assertAlmostEqual(order.amount_total,6,1,msg='Priceshouldbe11$-5$(discount)=6$')
        self.assertEqual(float_compare(order.amount_tax,6/11,precision_rounding=3),0,'10%Taxincludedin6$')

        sol.tax_id=self.tax_20pc_excl
        order.recompute_coupon_lines()

        self.assertEqual(order.amount_total,7,'Priceshouldbe12$-5$(discount)=7$')
        self.assertEqual(float_compare(order.amount_tax,7/12,precision_rounding=3),0,'20%Taxincludedon7$')

        sol.tax_id=self.tax_10pc_base_incl+self.tax_10pc_excl
        order.recompute_coupon_lines()

        self.assertAlmostEqual(order.amount_total,6,1,msg='Priceshouldbe11$-5$(discount)=6$')
        self.assertEqual(float_compare(order.amount_tax,6/12,precision_rounding=3),0,'20%Taxincludedon6$')

    deftest_fixed_amount_taxes_attribution_multiline(self):

        self.env['coupon.program'].create({
            'name':'$5coupon',
            'program_type':'promotion_program',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':5,
            'active':True,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order
        sol1=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        sol2=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()

        self.assertAlmostEqual(order.amount_total,15,1,msg='Priceshouldbe20$-5$(discount)=15$')
        self.assertEqual(order.amount_tax,0,'Notaxesareappliedyet')

        sol1.tax_id=self.tax_10pc_base_incl
        order.recompute_coupon_lines()

        self.assertAlmostEqual(order.amount_total,15,1,msg='Priceshouldbe20$-5$(discount)=15$')
        self.assertEqual(float_compare(order.amount_tax,5/11+0,precision_rounding=3),0,
                         '10%Taxincludedin5$insol1(highestcost)and0insol2')

        sol2.tax_id=self.tax_10pc_excl
        order.recompute_coupon_lines()

        self.assertAlmostEqual(order.amount_total,16,1,msg='Priceshouldbe21$-5$(discount)=16$')
        #Taxamount=10%in10$+10%in11$-10%in5$(applyonexcluded)
        self.assertEqual(float_compare(order.amount_tax,5/11,precision_rounding=3),0)

        sol2.tax_id=self.tax_10pc_base_incl+self.tax_10pc_excl
        order.recompute_coupon_lines()

        self.assertAlmostEqual(order.amount_total,16,1,msg='Priceshouldbe21$-5$(discount)=16$')
        #Promoapplyonline2(10%inc+10%exc)
        #Taxamount=10%in10$+10%in10$+10%in11-10%in5$-10%in4.55$(100/110*5)
        #           =10/11+10/11+11/11-5/11-4.55/11
        #           =21.45/11
        self.assertEqual(float_compare(order.amount_tax,21.45/11,precision_rounding=3),0)

        sol3=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })
        sol3.tax_id=self.tax_10pc_excl
        order.recompute_coupon_lines()

        self.assertAlmostEqual(order.amount_total,27,1,msg='Priceshouldbe32$-5$(discount)=27$')
        #Promoapplyonline2(10%inc+10%exc)
        #Taxamount=10%in10$+10%in10$+10%in11$+10%in11$-10%in5$-10%in4.55$(100/110*5)
        #           =10/11+10/11+11/11+11/11-5/11-4.55/11
        #           =32.45/11
        self.assertEqual(float_compare(order.amount_tax,32.45/11,precision_rounding=3),0)

    deftest_order_promo(self):

        promo_5off=self.env['coupon.program'].create({
            'name':'$5coupon',
            'program_type':'promotion_program',
            'promo_code_usage':'code_needed',
            'promo_code':'5off',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':5,
            'discount_apply_on':'on_order',
        })

        promo_20pc=self.env['coupon.program'].create({
            'name':'20%reductiononorder',
            'promo_code_usage':'no_code_needed',
            'promo_code':'20pc',
            'reward_type':'discount',
            'program_type':'promotion_program',
            'discount_type':'percentage',
            'discount_percentage':20.0,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order

        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        #Testpercentagethenflat
        order.recompute_coupon_lines()
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'5off')
        order.recompute_coupon_lines()

        self.assertEqual(order.amount_total,3,'Priceshouldbe10$-2$(20%of10$)-5$(flatdiscount)=3$')
        self.assertEqual(len(order.order_line),3,'Thereshouldbe3lines')

        order.order_line[1:].unlink()

        #Testflatthenpercentage
        promo_20pc.promo_code_usage='code_needed'
        promo_5off.promo_code_usage='no_code_needed'
        order.recompute_coupon_lines()
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'20pc')
        order.recompute_coupon_lines()

        self.assertEqual(order.amount_total,3,'Priceshouldbe10$-2$(20%of10$)-5$(flatdiscount)=3$')
        self.assertEqual(len(order.order_line),3,'Thereshouldbe3lines')

        #Testreapplyingalreadypresentpromo
        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order,'20pc')
        order.recompute_coupon_lines()

        self.assertEqual(order.amount_total,3,'Priceshouldbe10$-2$(20%of10$)-5$(flatdiscount)=3$')
        self.assertEqual(len(order.order_line),3,'Thereshouldbe3lines')

    deftest_fixed_amount_with_negative_cost(self):

        self.env['coupon.program'].create({
            'name':'$10coupon',
            'program_type':'promotion_program',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':10,
            'active':True,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order

        sol1=self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'name':'handdiscount',
            'price_unit':-5,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),3,'Promotionshouldadd1line')
        self.assertEqual(order.amount_total,0,'10$discountshouldcoverthewholeprice')

        sol1.price_unit=20
        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),3,'Promotionshouldadd1line')
        self.assertEqual(order.amount_total,5,'10$discountshouldbeappliedontopofthe15$originalprice')

    deftest_fixed_amount_with_tax_sale_order_amount_remain_positive(self):

        prod=self.env['coupon.program'].create({
            'name':'$10coupon',
            'program_type':'promotion_program',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':10,
            'active':True,
            'discount_apply_on':'on_order',
        })
        prod.discount_line_product_id.taxes_id=self.tax_15pc_excl

        order=self.empty_order
        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':5,
            'product_uom_qty':1.0,
            'order_id':order.id,
            'tax_id':self.tax_15pc_excl,
        })
        order.recompute_coupon_lines()
        self.assertEqual(order.amount_total,0,'SaleOrdertotalamountcannotbenegative')

    deftest_fixed_amount_change_promo_amount(self):

        promo=self.env['coupon.program'].create({
            'name':'$10coupon',
            'program_type':'promotion_program',
            'promo_code_usage':'no_code_needed',
            'reward_type':'discount',
            'discount_type':'fixed_amount',
            'discount_fixed_amount':10,
            'active':True,
            'discount_apply_on':'on_order',
        })

        order=self.empty_order

        self.env['sale.order.line'].create({
            'product_id':self.drawerBlack.id,
            'price_unit':10,
            'product_uom_qty':1.0,
            'order_id':order.id,
        })

        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),2,'Promotionshouldadd1line')
        self.assertEqual(order.amount_total,0,'10$-10$(discount)=0$(total)')

        promo.discount_fixed_amount=5
        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),2,'Promotionshouldadd1line')
        self.assertEqual(order.amount_total,5,'10$-5$(discount)=5$(total)')

        promo.discount_fixed_amount=0
        order.recompute_coupon_lines()

        self.assertEqual(len(order.order_line),1,'Promotionlineshouldnotbepresent')
        self.assertEqual(order.amount_total,10,'10$-0$(discount)=10$(total)')
