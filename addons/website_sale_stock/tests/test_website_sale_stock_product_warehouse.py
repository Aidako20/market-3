#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website.toolsimportMockRequest
fromflectra.addons.sale.tests.test_sale_product_attribute_value_configimportTestSaleProductAttributeValueCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestWebsiteSaleStockProductWarehouse(TestSaleProductAttributeValueCommon):

    @classmethod
    defsetUpClass(self):
        super().setUpClass()
        #Runthetestsinanothercompany,sothetestsdonotrelyonthe
        #databasestate(egthedefaultcompany'swarehouse)
        self.company=self.env['res.company'].create({'name':'CompanyC'})
        self.env.user.company_id=self.company
        self.website=self.env['website'].create({'name':'WebsiteCompanyC'})
        self.website.company_id=self.company

        #Settwowarehouses(onewascreatedoncompanycreation)
        self.warehouse_1=self.env['stock.warehouse'].search([('company_id','=',self.company.id)])
        self.warehouse_2=self.env['stock.warehouse'].create({
            'name':'Warehouse2',
            'code':'WH2'
        })

        #Createtwostockableproducts
        self.product_A=self.env['product.product'].create({
            'name':'ProductA',
            'inventory_availability':'always',
            'type':'product',
            'default_code':'E-COM1',
        })

        self.product_B=self.env['product.product'].create({
            'name':'ProductB',
            'inventory_availability':'always',
            'type':'product',
            'default_code':'E-COM2',
        })

        #Add10ProductAinWH1and15Product1inWH2
        self.env['stock.quant'].with_context(inventory_mode=True).create([{
            'product_id':self.product_A.id,
            'inventory_quantity':qty,
            'location_id':wh.lot_stock_id.id,
        }forwh,qtyin[(self.warehouse_1,10.0),(self.warehouse_2,15.0)]])

        #Add10Product2inWH2
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_B.id,
            'inventory_quantity':10.0,
            'location_id':self.warehouse_2.lot_stock_id.id,
        })

    deftest_01_get_combination_info(self):
        """Checkedthatcorrectproductquantityisshowninwebsiteaccording
        tothewarehousewhichissetincurrentwebsite.
          -SetWarehouse1,Warehouse2ornoneinwebsiteand:
            -CheckavailablequantityofProductAandProductBinwebsite
        Whentheuserdoesn'tsetanywarehouse,themoduleshouldstillselect
        adefaultone.
        """

        forwh,qty_a,qty_bin[(self.warehouse_1,10,0),(self.warehouse_2,15,10),(False,10,0)]:
            #setwarehouse_id
            self.website.warehouse_id=wh

            product=self.product_A.with_context(website_id=self.website.id)
            combination_info=product.product_tmpl_id.with_context(website_sale_stock_get_quantity=True)._get_combination_info()

            #Checkavailablequantityofproductisaccordingtowarehouse
            self.assertEqual(combination_info['virtual_available'],qty_a,"%sunitsofProductAshouldbeavailableinwarehouse%s"%(qty_a,wh))

            product=self.product_B.with_context(website_id=self.website.id)
            combination_info=product.product_tmpl_id.with_context(website_sale_stock_get_quantity=True)._get_combination_info()

            #Checkavailablequantityofproductisaccordingtowarehouse
            self.assertEqual(combination_info['virtual_available'],qty_b,"%sunitsofProductBshouldbeavailableinwarehouse%s"%(qty_b,wh))

    deftest_02_update_cart_with_multi_warehouses(self):
        """Whentheuserupdateshiscartandincreasesaproductquantity,if
        thisquantityisnotavailableintheSO'swarehouse,awarningshould
        bereturnedandthequantityupdatedtoitsmaximum."""

        so=self.env['sale.order'].create({
            'partner_id':self.env.user.partner_id.id,
            'order_line':[(0,0,{
                'name':self.product_A.name,
                'product_id':self.product_A.id,
                'product_uom_qty':5,
                'product_uom':self.product_A.uom_id.id,
                'price_unit':self.product_A.list_price,
            })]
        })

        withMockRequest(self.env,website=self.website,sale_order_id=so.id):
            website_so=self.website.sale_get_order()
            self.assertEqual(website_so.order_line.product_id.virtual_available,10,"ThisquantityshouldbebasedonSO'swarehouse")

            values=so._cart_update(product_id=self.product_A.id,line_id=so.order_line.id,set_qty=20)
            self.assertTrue(values.get('warning',False))
            self.assertEqual(values.get('quantity'),10)
