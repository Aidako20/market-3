#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.stock.tests.commonimportTestStockCommon


classTestReplenishWizard(TestStockCommon):
    defsetUp(self):
        super(TestReplenishWizard,self).setUp()
        self.vendor=self.env['res.partner'].create(dict(name='TheReplenisher'))
        self.product1_price=500

        #Createasupplierinfowitchthepreviousvendor
        self.supplierinfo=self.env['product.supplierinfo'].create({
            'name':self.vendor.id,
            'price':self.product1_price,
        })

        #Createaproductwiththe'buy'routeand
        #the'supplierinfo'prevouslycreated
        self.product1=self.env['product.product'].create({
            'name':'producta',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'seller_ids':[(4,self.supplierinfo.id,0)],
            'route_ids':[(4,self.env.ref('purchase_stock.route_warehouse0_buy').id,0)],
        })

        #AdditionalValuesrequiredbythereplenishwizard
        self.uom_unit=self.env.ref('uom.product_uom_unit')
        self.wh=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)

    deftest_replenish_buy_1(self):
        """Setaquantitytoreplenishviathe"Buy"routeandcheckif
        apurchaseorderiscreatedwiththecorrectvalues
        """
        self.product_uom_qty=42

        replenish_wizard=self.env['product.replenish'].create({
            'product_id':self.product1.id,
            'product_tmpl_id':self.product1.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'quantity':self.product_uom_qty,
            'warehouse_id':self.wh.id,
        })
        replenish_wizard.launch_replenishment()
        last_po_id=self.env['purchase.order'].search([
            ('origin','ilike','%ManualReplenishment%'),
            ('partner_id','=',self.vendor.id)
        ])[-1]
        self.assertTrue(last_po_id,'PurchaseOrdernotfound')
        order_line=last_po_id.order_line.search([('product_id','=',self.product1.id)])
        self.assertTrue(order_line,'TheproductisnotinthePurchaseOrder')
        self.assertEqual(order_line.product_qty,self.product_uom_qty,'Quantitiesdoesnotmatch')
        self.assertEqual(order_line.price_unit,self.product1_price,'Pricesdoesnotmatch')

    deftest_chose_supplier_1(self):
        """Choosesupplierbasedontheorderedquantityandminimumprice

        replenish10

        1)seq1vendor1140minqty1
        2)seq2vendor1100 minqty10
        ->2)shouldbechosen
        """
        product_to_buy=self.env['product.product'].create({
            'name':"FurnitureService",
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'route_ids':[(4,self.env.ref('purchase_stock.route_warehouse0_buy').id,0)],
        })
        vendor1=self.env['res.partner'].create({'name':'vendor1','email':'from.test@example.com'})

        supplierinfo1=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor1.id,
            'min_qty':1,
            'price':140,
            'sequence':1,
        })
        supplierinfo2=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor1.id,
            'min_qty':10,
            'price':100,
            'sequence':2,
        })

        replenish_wizard=self.env['product.replenish'].create({
            'product_id':product_to_buy.id,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'quantity':10,
            'warehouse_id':self.wh.id,
        })
        replenish_wizard.launch_replenishment()
        last_po_id=self.env['purchase.order'].search([
            ('origin','ilike','%ManualReplenishment%'),
        ])[-1]
        self.assertEqual(last_po_id.partner_id,vendor1)
        self.assertEqual(last_po_id.order_line.price_unit,100)

    deftest_chose_supplier_2(self):
        """Choosesupplierbasedontheorderedquantityandminimumprice

        replenish10

        1)seq1vendor1140minqty1
        2)seq2vendor290 minqty10
        3)seq3vendor1100minqty10
        ->3)shouldbechosen
        """
        product_to_buy=self.env['product.product'].create({
            'name':"FurnitureService",
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'route_ids':[(4,self.env.ref('purchase_stock.route_warehouse0_buy').id,0)],
        })
        vendor1=self.env['res.partner'].create({'name':'vendor1','email':'from.test@example.com'})
        vendor2=self.env['res.partner'].create({'name':'vendor2','email':'from.test2@example.com'})

        supplierinfo1=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor1.id,
            'min_qty':1,
            'price':140,
            'sequence':1,
        })
        supplierinfo2=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor2.id,
            'min_qty':10,
            'price':90,
            'sequence':2,
        })
        supplierinfo3=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor1.id,
            'min_qty':10,
            'price':100,
            'sequence':3,
        })

        replenish_wizard=self.env['product.replenish'].create({
            'product_id':product_to_buy.id,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'quantity':10,
            'warehouse_id':self.wh.id,
        })
        replenish_wizard.launch_replenishment()
        last_po_id=self.env['purchase.order'].search([
            ('origin','ilike','%ManualReplenishment%'),
        ])[-1]
        self.assertEqual(last_po_id.partner_id,vendor1)
        self.assertEqual(last_po_id.order_line.price_unit,100)

    deftest_chose_supplier_3(self):
        """Choosesupplierbasedontheorderedquantityandminimumprice

        replenish10

        1)seq2vendor150
        2)seq1vendor250
        ->2)shouldbechosen
        """
        product_to_buy=self.env['product.product'].create({
            'name':"FurnitureService",
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'route_ids':[(4,self.env.ref('purchase_stock.route_warehouse0_buy').id,0)],
        })
        vendor1=self.env['res.partner'].create({'name':'vendor1','email':'from.test@example.com'})
        vendor2=self.env['res.partner'].create({'name':'vendor2','email':'from.test2@example.com'})

        supplierinfo1=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor1.id,
            'price':50,
            'sequence':2,
        })
        supplierinfo2=self.env['product.supplierinfo'].create({
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'name':vendor2.id,
            'price':50,
            'sequence':1,
        })

        replenish_wizard=self.env['product.replenish'].create({
            'product_id':product_to_buy.id,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'quantity':10,
            'warehouse_id':self.wh.id,
        })
        replenish_wizard.launch_replenishment()
        last_po_id=self.env['purchase.order'].search([
            ('origin','ilike','%ManualReplenishment%'),
        ])[-1]
        self.assertEqual(last_po_id.partner_id,vendor2)

    deftest_chose_supplier_4(self):
        """Choosesupplierbasedontheorderedquantityandminimumprice

        replenish10

        1)seq1vendor1100minqty2
        2)seq2vendor160minqty10
        2)seq3vendor180minqty5
        ->2)shouldbechosen
        """
        product_to_buy=self.env['product.product'].create({
            'name':"FurnitureService",
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
            'route_ids':[(4,self.env.ref('purchase_stock.route_warehouse0_buy').id,0)],
        })
        vendor1=self.env['res.partner'].create({'name':'vendor1','email':'from.test@example.com'})
        supplierinfo1=self.env['product.supplierinfo'].create({
            'name':vendor1.id,
            'price':100,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'min_qty':2
        })
        supplierinfo2=self.env['product.supplierinfo'].create({
            'name':vendor1.id,
            'price':60,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'min_qty':10
        })
        supplierinfo3=self.env['product.supplierinfo'].create({
            'name':vendor1.id,
            'price':80,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'min_qty':5
        })
        replenish_wizard=self.env['product.replenish'].create({
            'product_id':product_to_buy.id,
            'product_tmpl_id':product_to_buy.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'quantity':10,
            'warehouse_id':self.wh.id,
        })
        replenish_wizard.launch_replenishment()
        last_po_id=self.env['purchase.order'].search([
            ('origin','ilike','%ManualReplenishment%'),
        ])[-1]

        self.assertEqual(last_po_id.partner_id,vendor1)
        self.assertEqual(last_po_id.order_line.price_unit,60)
