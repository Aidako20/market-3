#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.tests.commonimportTransactionCase


classTestOnchangeProductId(TransactionCase):
    """Testthatwhenanincludedtaxismappedbyafiscalposition,theincludedtaxmustbe
    subtractedtothepriceoftheproduct.
    """

    defsetUp(self):
        super(TestOnchangeProductId,self).setUp()
        self.fiscal_position_model=self.env['account.fiscal.position']
        self.fiscal_position_tax_model=self.env['account.fiscal.position.tax']
        self.tax_model=self.env['account.tax']
        self.so_model=self.env['sale.order']
        self.po_line_model=self.env['sale.order.line']
        self.res_partner_model=self.env['res.partner']
        self.product_tmpl_model=self.env['product.template']
        self.product_model=self.env['product.product']
        self.product_uom_model=self.env['uom.uom']
        self.supplierinfo_model=self.env["product.supplierinfo"]
        self.pricelist_model=self.env['product.pricelist']

    deftest_onchange_product_id(self):

        uom_id=self.product_uom_model.search([('name','=','Units')])[0]
        pricelist=self.pricelist_model.search([('name','=','PublicPricelist')])[0]

        partner_id=self.res_partner_model.create(dict(name="George"))
        tax_include_id=self.tax_model.create(dict(name="Includetax",
                                                    amount='21.00',
                                                    price_include=True,
                                                    type_tax_use='sale'))
        tax_exclude_id=self.tax_model.create(dict(name="Excludetax",
                                                    amount='0.00',
                                                    type_tax_use='sale'))

        product_tmpl_id=self.product_tmpl_model.create(dict(name="Voiture",
                                                              list_price=121,
                                                              taxes_id=[(6,0,[tax_include_id.id])]))

        product_id=product_tmpl_id.product_variant_id

        fp_id=self.fiscal_position_model.create(dict(name="fiscalposition",sequence=1))

        fp_tax_id=self.fiscal_position_tax_model.create(dict(position_id=fp_id.id,
                                                               tax_src_id=tax_include_id.id,
                                                               tax_dest_id=tax_exclude_id.id))

        #CreatetheSOwithoneSOlineandapplyapricelistandfiscalpositiononit
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner_id
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fp_id
        withorder_form.order_line.new()asline:
            line.name=product_id.name
            line.product_id=product_id
            line.product_uom_qty=1.0
            line.product_uom=uom_id
        sale_order=order_form.save()

        #ChecktheunitpriceofSOline
        self.assertEqual(100,sale_order.order_line[0].price_unit,"Theincludedtaxmustbesubtractedtotheprice")

    deftest_fiscalposition_application(self):
        """Testapplicationofafiscalpositionmapping
        priceincludedtopriceincludedtax
        """

        uom=self.product_uom_model.search([('name','=','Units')])
        pricelist=self.pricelist_model.search([('name','=','PublicPricelist')])

        partner=self.res_partner_model.create({
            'name':"George"
        })
        tax_fixed_incl=self.tax_model.create({
            'name':"fixedinclude",
            'amount':'10.00',
            'amount_type':'fixed',
            'price_include':True,
        })
        tax_fixed_excl=self.tax_model.create({
            'name':"fixedexclude",
            'amount':'10.00',
            'amount_type':'fixed',
            'price_include':False,
        })
        tax_include_src=self.tax_model.create({
            'name':"Include21%",
            'amount':21.00,
            'amount_type':'percent',
            'price_include':True,
        })
        tax_include_dst=self.tax_model.create({
            'name':"Include6%",
            'amount':6.00,
            'amount_type':'percent',
            'price_include':True,
        })
        tax_exclude_src=self.tax_model.create({
            'name':"Exclude15%",
            'amount':15.00,
            'amount_type':'percent',
            'price_include':False,
        })
        tax_exclude_dst=self.tax_model.create({
            'name':"Exclude21%",
            'amount':21.00,
            'amount_type':'percent',
            'price_include':False,
        })
        product_tmpl_a=self.product_tmpl_model.create({
            'name':"Voiture",
            'list_price':121,
            'taxes_id':[(6,0,[tax_include_src.id])]
        })

        product_tmpl_b=self.product_tmpl_model.create({
            'name':"Voiture",
            'list_price':100,
            'taxes_id':[(6,0,[tax_exclude_src.id])]
        })

        product_tmpl_c=self.product_tmpl_model.create({
            'name':"Voiture",
            'list_price':100,
            'taxes_id':[(6,0,[tax_fixed_incl.id,tax_exclude_src.id])]
        })

        product_tmpl_d=self.product_tmpl_model.create({
            'name':"Voiture",
            'list_price':100,
            'taxes_id':[(6,0,[tax_fixed_excl.id,tax_include_src.id])]
        })

        fpos_incl_incl=self.fiscal_position_model.create({
            'name':"incl->incl",
            'sequence':1
        })

        self.fiscal_position_tax_model.create({
            'position_id':fpos_incl_incl.id,
            'tax_src_id':tax_include_src.id,
            'tax_dest_id':tax_include_dst.id
        })

        fpos_excl_incl=self.fiscal_position_model.create({
            'name':"excl->incl",
            'sequence':2,
        })

        self.fiscal_position_tax_model.create({
            'position_id':fpos_excl_incl.id,
            'tax_src_id':tax_exclude_src.id,
            'tax_dest_id':tax_include_dst.id
        })

        fpos_incl_excl=self.fiscal_position_model.create({
            'name':"incl->excl",
            'sequence':3,
        })

        self.fiscal_position_tax_model.create({
            'position_id':fpos_incl_excl.id,
            'tax_src_id':tax_include_src.id,
            'tax_dest_id':tax_exclude_dst.id
        })

        fpos_excl_excl=self.fiscal_position_model.create({
            'name':"excl->excp",
            'sequence':4,
        })

        self.fiscal_position_tax_model.create({
            'position_id':fpos_excl_excl.id,
            'tax_src_id':tax_exclude_src.id,
            'tax_dest_id':tax_exclude_dst.id
        })

        #CreatetheSOwithoneSOlineandapplyapricelistandfiscalpositiononit
        #Thencheckifpriceunitandpricesubtotalmatchestheexpectedvalues

        #TestMappingincludedtoincluded
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fpos_incl_incl
        withorder_form.order_line.new()asline:
            line.name=product_tmpl_a.product_variant_id.name
            line.product_id=product_tmpl_a.product_variant_id
            line.product_uom_qty=1.0
            line.product_uom=uom
        sale_order=order_form.save()
        self.assertRecordValues(sale_order.order_line,[{'price_unit':106,'price_subtotal':100}])

        #TestMappingexcludedtoincluded
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fpos_excl_incl
        withorder_form.order_line.new()asline:
            line.name=product_tmpl_b.product_variant_id.name
            line.product_id=product_tmpl_b.product_variant_id
            line.product_uom_qty=1.0
            line.product_uom=uom
        sale_order=order_form.save()
        self.assertRecordValues(sale_order.order_line,[{'price_unit':100,'price_subtotal':94.34}])

        #TestMappingincludedtoexcluded
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fpos_incl_excl
        withorder_form.order_line.new()asline:
            line.name=product_tmpl_a.product_variant_id.name
            line.product_id=product_tmpl_a.product_variant_id
            line.product_uom_qty=1.0
            line.product_uom=uom
        sale_order=order_form.save()
        self.assertRecordValues(sale_order.order_line,[{'price_unit':100,'price_subtotal':100}])

        #TestMappingexcludedtoexcluded
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fpos_excl_excl
        withorder_form.order_line.new()asline:
            line.name=product_tmpl_b.product_variant_id.name
            line.product_id=product_tmpl_b.product_variant_id
            line.product_uom_qty=1.0
            line.product_uom=uom
        sale_order=order_form.save()
        self.assertRecordValues(sale_order.order_line,[{'price_unit':100,'price_subtotal':100}])

        #TestMapping(included,excluded)to(included,included)
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fpos_excl_incl
        withorder_form.order_line.new()asline:
            line.name=product_tmpl_c.product_variant_id.name
            line.product_id=product_tmpl_c.product_variant_id
            line.product_uom_qty=1.0
            line.product_uom=uom
        sale_order=order_form.save()
        self.assertRecordValues(sale_order.order_line,[{'price_unit':100,'price_subtotal':84.91}])

        #TestMapping(excluded,included)to(excluded,excluded)
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.pricelist_id=pricelist
        order_form.fiscal_position_id=fpos_incl_excl
        withorder_form.order_line.new()asline:
            line.name=product_tmpl_d.product_variant_id.name
            line.product_id=product_tmpl_d.product_variant_id
            line.product_uom_qty=1.0
            line.product_uom=uom
        sale_order=order_form.save()
        self.assertRecordValues(sale_order.order_line,[{'price_unit':100,'price_subtotal':100}])

    deftest_pricelist_application(self):
        """Testdifferentpricesarecorrectlyappliedbasedondates"""
        support_product=self.env['product.product'].create({
            'name':'VirtualHomeStaging',
            'list_price':100,
        })
        partner=self.res_partner_model.create(dict(name="George"))

        christmas_pricelist=self.env['product.pricelist'].create({
            'name':'Christmaspricelist',
            'item_ids':[(0,0,{
                'date_start':"2017-12-01",
                'date_end':"2017-12-24",
                'compute_price':'percentage',
                'base':'list_price',
                'percent_price':20,
                'applied_on':'3_global',
                'name':'Pre-Christmasdiscount'
            }),(0,0,{
                'date_start':"2017-12-25",
                'date_end':"2017-12-31",
                'compute_price':'percentage',
                'base':'list_price',
                'percent_price':50,
                'applied_on':'3_global',
                'name':'Post-Christmassuper-discount'
            })]
        })

        #CreatetheSOwithpricelistbasedondate
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=partner
        order_form.date_order='2017-12-20'
        order_form.pricelist_id=christmas_pricelist
        withorder_form.order_line.new()asline:
            line.product_id=support_product
        so=order_form.save()
        #ChecktheunitpriceandsubtotalofSOline
        self.assertEqual(so.order_line[0].price_unit,80,"Firstdatepricelistrulenotapplied")
        self.assertEqual(so.order_line[0].price_subtotal,so.order_line[0].price_unit*so.order_line[0].product_uom_qty,'TotalofSOlineshouldbeamultiplicationofunitpriceandorderedquantity')

        #ChangeorderdateoftheSOandchecktheunitpriceandsubtotalofSOline
        withForm(so)asorder:
            order.date_order='2017-12-30'
            withorder.order_line.edit(0)asline:
                line.product_id=support_product

        self.assertEqual(so.order_line[0].price_unit,50,"Seconddatepricelistrulenotapplied")
        self.assertEqual(so.order_line[0].price_subtotal,so.order_line[0].price_unit*so.order_line[0].product_uom_qty,'TotalofSOlineshouldbeamultiplicationofunitpriceandorderedquantity')

    deftest_pricelist_uom_discount(self):
        """Testpricesanddiscountsarecorrectlyappliedbasedondateanduom"""
        computer_case=self.env['product.product'].create({
            'name':'DrawerBlack',
            'list_price':100,
        })
        partner=self.res_partner_model.create(dict(name="George"))
        categ_unit_id=self.ref('uom.product_uom_categ_unit')
        goup_discount_id=self.ref('product.group_discount_per_so_line')
        self.env.user.write({'groups_id':[(4,goup_discount_id,0)]})
        new_uom=self.env['uom.uom'].create({
            'name':'10units',
            'factor_inv':10,
            'uom_type':'bigger',
            'rounding':1.0,
            'category_id':categ_unit_id
        })
        christmas_pricelist=self.env['product.pricelist'].create({
            'name':'Christmaspricelist',
            'discount_policy':'without_discount',
            'item_ids':[(0,0,{
                'date_start':"2017-12-01",
                'date_end':"2017-12-30",
                'compute_price':'percentage',
                'base':'list_price',
                'percent_price':10,
                'applied_on':'3_global',
                'name':'Christmasdiscount'
            })]
        })

        so=self.env['sale.order'].create({
            'partner_id':partner.id,
            'date_order':'2017-12-20',
            'pricelist_id':christmas_pricelist.id,
        })

        order_line=self.env['sale.order.line'].new({
            'order_id':so.id,
            'product_id':computer_case.id,
        })

        #forcecomputeuomandprices
        order_line.product_id_change()
        order_line.product_uom_change()
        order_line._onchange_discount()
        self.assertEqual(order_line.price_subtotal,90,"Christmasdiscountpricelistrulenotapplied")
        self.assertEqual(order_line.discount,10,"Christmasdiscountnotequaltto10%")
        order_line.product_uom=new_uom
        order_line.product_uom_change()
        order_line._onchange_discount()
        self.assertEqual(order_line.price_subtotal,900,"Christmasdiscountpricelistrulenotapplied")
        self.assertEqual(order_line.discount,10,"Christmasdiscountnotequaltto10%")

    deftest_pricelist_based_on_other(self):
        """Testpriceanddiscountarecorrectlyappliedwithapricelistbasedonanotherone"""
        computer_case=self.env['product.product'].create({
            'name':'DrawerBlack',
            'list_price':100,
        })
        partner=self.res_partner_model.create(dict(name="George"))
        goup_discount_id=self.ref('product.group_discount_per_so_line')
        self.env.user.write({'groups_id':[(4,goup_discount_id,0)]})

        first_pricelist=self.env['product.pricelist'].create({
            'name':'Firstpricelist',
            'discount_policy':'without_discount',
            'item_ids':[(0,0,{
                'compute_price':'percentage',
                'base':'list_price',
                'percent_price':10,
                'applied_on':'3_global',
                'name':'Firstdiscount'
            })]
        })

        second_pricelist=self.env['product.pricelist'].create({
            'name':'Secondpricelist',
            'discount_policy':'without_discount',
            'item_ids':[(0,0,{
                'compute_price':'formula',
                'base':'pricelist',
                'base_pricelist_id':first_pricelist.id,
                'price_discount':10,
                'applied_on':'3_global',
                'name':'Seconddiscount'
            })]
        })

        so=self.env['sale.order'].create({
            'partner_id':partner.id,
            'date_order':'2018-07-11',
            'pricelist_id':second_pricelist.id,
        })

        order_line=self.env['sale.order.line'].new({
            'order_id':so.id,
            'product_id':computer_case.id,
        })

        #forcecomputeuomandprices
        order_line.product_id_change()
        order_line._onchange_discount()
        self.assertEqual(order_line.price_subtotal,81,"Secondpricelistrulenotapplied")
        self.assertEqual(order_line.discount,19,"Seconddiscountnotapplied")

    deftest_pricelist_with_other_currency(self):
        """Testpricesarecorrectlyappliedwithapricelistwithanothercurrency"""
        computer_case=self.env['product.product'].create({
            'name':'DrawerBlack',
            'list_price':100,
        })
        computer_case.list_price=100
        partner=self.res_partner_model.create(dict(name="George"))
        categ_unit_id=self.ref('uom.product_uom_categ_unit')
        other_currency=self.env['res.currency'].create({'name':'othercurrency',
            'symbol':'other'})
        self.env['res.currency.rate'].create({'name':'2018-07-11',
            'rate':2.0,
            'currency_id':other_currency.id,
            'company_id':self.env.company.id})
        self.env['res.currency.rate'].search(
            [('currency_id','=',self.env.company.currency_id.id)]
        ).unlink()
        new_uom=self.env['uom.uom'].create({
            'name':'10units',
            'factor_inv':10,
            'uom_type':'bigger',
            'rounding':1.0,
            'category_id':categ_unit_id
        })

        #Thispricelistdoesn'tshowthediscount
        first_pricelist=self.env['product.pricelist'].create({
            'name':'Firstpricelist',
            'currency_id':other_currency.id,
            'discount_policy':'with_discount',
            'item_ids':[(0,0,{
                'compute_price':'percentage',
                'base':'list_price',
                'percent_price':10,
                'applied_on':'3_global',
                'name':'Firstdiscount'
            })]
        })

        so=self.env['sale.order'].create({
            'partner_id':partner.id,
            'date_order':'2018-07-12',
            'pricelist_id':first_pricelist.id,
        })

        order_line=self.env['sale.order.line'].new({
            'order_id':so.id,
            'product_id':computer_case.id,
        })

        #forcecomputeuomandprices
        order_line.product_id_change()
        self.assertEqual(order_line.price_unit,180,"Firstpricelistrulenotapplied")
        order_line.product_uom=new_uom
        order_line.product_uom_change()
        self.assertEqual(order_line.price_unit,1800,"Firstpricelistrulenotapplied")
