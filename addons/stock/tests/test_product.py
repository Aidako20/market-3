#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#Author:LeonardoPistone
#Copyright2015CamptocampSA

fromflectra.addons.stock.tests.common2importTestStockCommon
fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportForm


classTestVirtualAvailable(TestStockCommon):
    defsetUp(self):
        super(TestVirtualAvailable,self).setUp()

        #Make`product3`astorableproductforthistest.Indeed,creatingquants
        #andplayingwithownersisnotpossibleforconsumables.
        self.product_3.type='product'

        self.env['stock.quant'].create({
            'product_id':self.product_3.id,
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'quantity':30.0})

        self.env['stock.quant'].create({
            'product_id':self.product_3.id,
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'quantity':10.0,
            'owner_id':self.user_stock_user.partner_id.id})

        self.picking_out=self.env['stock.picking'].create({
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id})
        self.env['stock.move'].create({
            'name':'amove',
            'product_id':self.product_3.id,
            'product_uom_qty':3.0,
            'product_uom':self.product_3.uom_id.id,
            'picking_id':self.picking_out.id,
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id})

        self.picking_out_2=self.env['stock.picking'].create({
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id})
        self.env['stock.move'].create({
            'restrict_partner_id':self.user_stock_user.partner_id.id,
            'name':'anothermove',
            'product_id':self.product_3.id,
            'product_uom_qty':5.0,
            'product_uom':self.product_3.uom_id.id,
            'picking_id':self.picking_out_2.id,
            'location_id':self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':self.env.ref('stock.stock_location_customers').id})

    deftest_without_owner(self):
        self.assertAlmostEqual(40.0,self.product_3.virtual_available)
        self.picking_out.action_assign()
        self.picking_out_2.action_assign()
        self.assertAlmostEqual(32.0,self.product_3.virtual_available)

    deftest_with_owner(self):
        prod_context=self.product_3.with_context(owner_id=self.user_stock_user.partner_id.id)
        self.assertAlmostEqual(10.0,prod_context.virtual_available)
        self.picking_out.action_assign()
        self.picking_out_2.action_assign()
        self.assertAlmostEqual(5.0,prod_context.virtual_available)

    deftest_free_quantity(self):
        """Testthevalueofproduct.free_qty.Free_qty=qty_on_hand-qty_reserved"""
        self.assertAlmostEqual(40.0,self.product_3.free_qty)
        self.picking_out.action_confirm()
        self.picking_out_2.action_confirm()
        #Noreservationsofree_qtyisunchanged
        self.assertAlmostEqual(40.0,self.product_3.free_qty)
        self.picking_out.action_assign()
        self.picking_out_2.action_assign()
        #8unitsarenowreserved
        self.assertAlmostEqual(32.0,self.product_3.free_qty)
        self.picking_out.do_unreserve()
        self.picking_out_2.do_unreserve()
        #8unitsareavailableagain
        self.assertAlmostEqual(40.0,self.product_3.free_qty)

    deftest_archive_product_1(self):
        """`qty_available`and`virtual_available`arecomputedonarchivedproducts"""
        self.assertTrue(self.product_3.active)
        self.assertAlmostEqual(40.0,self.product_3.qty_available)
        self.assertAlmostEqual(40.0,self.product_3.virtual_available)
        self.product_3.active=False
        self.assertAlmostEqual(40.0,self.product_3.qty_available)
        self.assertAlmostEqual(40.0,self.product_3.virtual_available)

    deftest_archive_product_2(self):
        """Archivingaproductshouldarchiveitsreorderingrules"""
        self.assertTrue(self.product_3.active)
        orderpoint_form=Form(self.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id=self.product_3
        orderpoint_form.location_id=self.env.ref('stock.stock_location_stock')
        orderpoint_form.product_min_qty=0.0
        orderpoint_form.product_max_qty=5.0
        orderpoint=orderpoint_form.save()
        self.assertTrue(orderpoint.active)
        self.product_3.active=False
        self.assertFalse(orderpoint.active)

    deftest_change_product_company(self):
        """Checkswecan'tchangetheproduct'scompanyifthisproducthas
        quantinanothercompany."""
        company1=self.env.ref('base.main_company')
        company2=self.env['res.company'].create({'name':'SecondCompany'})
        product=self.env['product.product'].create({
            'name':'Product[TEST-ChangeCompany]',
            'type':'product',
        })
        #CreatesaquantforproductAinthefirstcompany.
        self.env['stock.quant'].create({
            'product_id':product.id,
            'product_uom_id':self.uom_unit.id,
            'location_id':self.location_1.id,
            'quantity':7,
            'reserved_quantity':0,
        })
        #Assignsacompany:shouldbeOKforcompany1butshouldraiseanerrorforcompany2.
        product.company_id=company1.id
        withself.assertRaises(UserError):
            product.company_id=company2.id
        #Checkswecanassingcompany2fortheproductoncethereisnomorequantforit.
        quant=self.env['stock.quant'].search([('product_id','=',product.id)])
        quant.quantity=0
        self.env['stock.quant']._unlink_zero_quants()
        product.company_id=company2.id #Shouldworkthistime.

    deftest_change_product_company_02(self):
        """Checkswecan'tchangetheproduct'scompanyifthisproducthas
        stockmovelineinanothercompany."""
        company1=self.env.ref('base.main_company')
        company2=self.env['res.company'].create({'name':'SecondCompany'})
        product=self.env['product.product'].create({
            'name':'Product[TEST-ChangeCompany]',
            'type':'consu',
        })
        picking=self.env['stock.picking'].create({
            'location_id':self.env.ref('stock.stock_location_customers').id,
            'location_dest_id':self.env.ref('stock.stock_location_stock').id,
            'picking_type_id':self.ref('stock.picking_type_in'),
        })
        self.env['stock.move'].create({
            'name':'test',
            'location_id':self.env.ref('stock.stock_location_customers').id,
            'location_dest_id':self.env.ref('stock.stock_location_stock').id,
            'product_id':product.id,
            'product_uom':product.uom_id.id,
            'product_uom_qty':1,
            'picking_id':picking.id,
        })
        picking.action_confirm()
        wizard_data=picking.button_validate()
        wizard=Form(self.env[wizard_data['res_model']].with_context(wizard_data['context'])).save()
        wizard.process()

        product.company_id=company1.id
        withself.assertRaises(UserError):
            product.company_id=company2.id

    deftest_change_product_company_exclude_vendor_and_customer_location(self):
        """Checkswecanchangeproductcompanywhereonlyexistsinglecompany
        andexistquantinvendor/customerlocation"""
        company1=self.env.ref('base.main_company')
        customer_location=self.env.ref('stock.stock_location_customers')
        supplier_location=self.env.ref('stock.stock_location_suppliers')
        product=self.env['product.product'].create({
            'name':'ProductSingleCompany',
            'type':'product',
        })
        #Createsaquantforcompany1.
        self.env['stock.quant'].create({
            'product_id':product.id,
            'product_uom_id':self.uom_unit.id,
            'location_id':self.location_1.id,
            'quantity':5,
        })
        #Createsaquantforvendorlocation.
        self.env['stock.quant'].create({
            'product_id':product.id,
            'product_uom_id':self.uom_unit.id,
            'location_id':supplier_location.id,
            'quantity':-15,
        })
        #Createsaquantforcustomerlocation.
        self.env['stock.quant'].create({
            'product_id':product.id,
            'product_uom_id':self.uom_unit.id,
            'location_id':customer_location.id,
            'quantity':10,
        })
        #Assignsacompany:shouldbeokbecauseonlyexistonecompany(excludevendorandcustomerlocation)
        product.company_id=company1.id

        #Resetproductcompanytoempty
        product.company_id=False
        company2=self.env['res.company'].create({'name':'SecondCompany'})
        #Assignstoanothercompany:shouldbenotokaybecauseexistquantsindefferentcompany(excludevendorandcustomerlocation)
        withself.assertRaises(UserError):
            product.company_id=company2.id

    deftest_search_qty_available(self):
        product=self.env['product.product'].create({
            'name':'Brandnewproduct',
            'type':'product',
        })
        result=self.env['product.product'].search([
            ('qty_available','=',0),
            ('id','in',product.ids),
        ])
        self.assertEqual(product,result)

    deftest_search_product_template(self):
        """
        SupposeavariantV01thatcannotbedeletedbecauseitisusedbya
        lot[1].Then,thevariant'stemplateTischanged:weaddadynamic
        attribute.Becauseof[1],V01isarchived.Thistestensuresthat
        `name_search`stillfindsT.
        Then,wecreateanewvariantV02ofT.Thistestalsoensuresthat
        calling`name_search`withanegativeoperatorwillexcludeTfromthe
        result.
        """
        template=self.env['product.template'].create({
            'name':'SuperProduct',
        })
        product01=template.product_variant_id

        self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':product01.id,
            'company_id':self.env.company.id,
        })

        product_attribute=self.env['product.attribute'].create({
            'name':'PA',
            'create_variant':'dynamic'
        })

        self.env['product.attribute.value'].create([{
            'name':'PAV'+str(i),
            'attribute_id':product_attribute.id
        }foriinrange(2)])

        tmpl_attr_lines=self.env['product.template.attribute.line'].create({
            'attribute_id':product_attribute.id,
            'product_tmpl_id':product01.product_tmpl_id.id,
            'value_ids':[(6,0,product_attribute.value_ids.ids)],
        })

        self.assertFalse(product01.active)
        self.assertTrue(template.active)
        self.assertFalse(template.product_variant_ids)

        res=self.env['product.template'].name_search(name='super',operator='ilike')
        res_ids=[r[0]forrinres]
        self.assertIn(template.id,res_ids)

        product02=self.env['product.product'].create({
            'default_code':'123',
            'product_tmpl_id':template.id,
            'product_template_attribute_value_ids':[(6,0,tmpl_attr_lines.product_template_value_ids[0].ids)]
        })

        self.assertFalse(product01.active)
        self.assertTrue(product02.active)
        self.assertTrue(template)
        self.assertEqual(template.product_variant_ids,product02)

        res=self.env['product.template'].name_search(name='123',operator='notilike')
        res_ids=[r[0]forrinres]
        self.assertNotIn(template.id,res_ids)

    deftest_change_type_tracked_product(self):
        product=self.env['product.template'].create({
            'name':'Brandnewproduct',
            'type':'product',
            'tracking':'serial',
        })
        product_form=Form(product)
        product_form.type='service'
        product=product_form.save()
        self.assertEqual(product.tracking,'none')

        product.type='product'
        product.tracking='serial'
        self.assertEqual(product.tracking,'serial')
        product_form=Form(product.product_variant_id)
        product_form.type='service'
        product=product_form.save()
        self.assertEqual(product.tracking,'none')
