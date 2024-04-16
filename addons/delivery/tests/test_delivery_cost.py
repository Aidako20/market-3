#-*-coding:utf-8-*-

fromflectra.testsimportcommon,Form
fromflectra.toolsimportfloat_compare


@common.tagged('post_install','-at_install')
classTestDeliveryCost(common.TransactionCase):

    defsetUp(self):
        super(TestDeliveryCost,self).setUp()
        self.SaleOrder=self.env['sale.order']
        self.SaleOrderLine=self.env['sale.order.line']
        self.AccountAccount=self.env['account.account']
        self.SaleConfigSetting=self.env['res.config.settings']
        self.Product=self.env['product.product']

        self.partner_18=self.env['res.partner'].create({'name':'MyTestCustomer'})
        self.pricelist=self.env.ref('product.list0')
        self.product_4=self.env['product.product'].create({'name':'Aproducttodeliver','weight':1.0})
        self.product_uom_unit=self.env.ref('uom.product_uom_unit')
        self.product_delivery_normal=self.env['product.product'].create({
            'name':'NormalDeliveryCharges',
            'type':'service',
            'list_price':10.0,
            'categ_id':self.env.ref('delivery.product_category_deliveries').id,
        })
        self.normal_delivery=self.env['delivery.carrier'].create({
            'name':'NormalDeliveryCharges',
            'fixed_price':10,
            'delivery_type':'fixed',
            'product_id':self.product_delivery_normal.id,
        })
        self.partner_4=self.env['res.partner'].create({'name':'AnotherCustomer'})
        self.partner_address_13=self.env['res.partner'].create({
            'name':"AnotherCustomer'sAddress",
            'parent_id':self.partner_4.id,
        })
        self.product_uom_hour=self.env.ref('uom.product_uom_hour')
        self.account_data=self.env.ref('account.data_account_type_revenue')
        self.account_tag_operating=self.env.ref('account.account_tag_operating')
        self.product_2=self.env['product.product'].create({'name':'Zizizaproduct','weight':1.0})
        self.product_category=self.env.ref('product.product_category_all')
        self.free_delivery=self.env.ref('delivery.free_delivery_carrier')
        #asthetestshereunderassumeallthepricesinUSD,wemustensure
        #thatthecompanyactuallyusesUSD
        #Wedoaninvalidate_cachesothecacheisawareofittoo.
        self.env.cr.execute(
            "UPDATEres_companySETcurrency_id=%sWHEREid=%s",
            [self.env.ref('base.USD').id,self.env.company.id])
        self.env.company.invalidate_cache()
        self.pricelist.currency_id=self.env.ref('base.USD').id

    deftest_00_delivery_cost(self):
        #InordertotestCarrierCost
        #CreatesalesorderwithNormalDeliveryCharges

        self.sale_normal_delivery_charges=self.SaleOrder.create({
            'partner_id':self.partner_18.id,
            'partner_invoice_id':self.partner_18.id,
            'partner_shipping_id':self.partner_18.id,
            'pricelist_id':self.pricelist.id,
            'order_line':[(0,0,{
                'name':'PCAssamble+2GBRAM',
                'product_id':self.product_4.id,
                'product_uom_qty':1,
                'product_uom':self.product_uom_unit.id,
                'price_unit':750.00,
            })],
        })
        #IadddeliverycostinSalesorder

        self.a_sale=self.AccountAccount.create({
            'code':'X2020',
            'name':'ProductSales-(test)',
            'user_type_id':self.account_data.id,
            'tag_ids':[(6,0,{
                self.account_tag_operating.id
            })]
        })

        self.product_consultant=self.Product.create({
            'sale_ok':True,
            'list_price':75.0,
            'standard_price':30.0,
            'uom_id':self.product_uom_hour.id,
            'uom_po_id':self.product_uom_hour.id,
            'name':'Service',
            'categ_id':self.product_category.id,
            'type':'service'
        })

        #IadddeliverycostinSalesorder
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id':self.sale_normal_delivery_charges.id,
            'default_carrier_id':self.normal_delivery.id
        }))
        choose_delivery_carrier=delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        #Ichecksalesorderafteraddeddeliverycost

        line=self.SaleOrderLine.search([('order_id','=',self.sale_normal_delivery_charges.id),
            ('product_id','=',self.normal_delivery.product_id.id)])
        self.assertEqual(len(line),1,"DeliverycostisnotAdded")

        zin=str(delivery_wizard.display_price)+""+str(delivery_wizard.delivery_price)+''+line.company_id.country_id.code+line.company_id.name
        self.assertEqual(float_compare(line.price_subtotal,10.0,precision_digits=2),0,
            "Deliverycostdoesnotcorrespondto10.0.%s%s"%(line.price_subtotal,zin))

        #Iconfirmthesalesorder

        self.sale_normal_delivery_charges.action_confirm()

        #CreateonemoresalesorderwithFreeDeliveryCharges

        self.delivery_sale_order_cost=self.SaleOrder.create({
            'partner_id':self.partner_4.id,
            'partner_invoice_id':self.partner_address_13.id,
            'partner_shipping_id':self.partner_address_13.id,
            'pricelist_id':self.pricelist.id,
            'order_line':[(0,0,{
                'name':'Serviceondemand',
                'product_id':self.product_consultant.id,
                'product_uom_qty':24,
                'product_uom':self.product_uom_hour.id,
                'price_unit':75.00,
            }),(0,0,{
                'name':'OnSiteAssistance',
                'product_id':self.product_2.id,
                'product_uom_qty':30,
                'product_uom':self.product_uom_unit.id,
                'price_unit':38.25,
            })],
        })

        #IaddfreedeliverycostinSalesorder
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id':self.delivery_sale_order_cost.id,
            'default_carrier_id':self.free_delivery.id
        }))
        choose_delivery_carrier=delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        #Ichecksalesorderafteraddingdeliverycost
        line=self.SaleOrderLine.search([('order_id','=',self.delivery_sale_order_cost.id),
            ('product_id','=',self.free_delivery.product_id.id)])

        self.assertEqual(len(line),1,"DeliverycostisnotAdded")
        self.assertEqual(float_compare(line.price_subtotal,0,precision_digits=2),0,
            "Deliverycostisnotcorrespond.")

        #Isetdefaultdeliverypolicy

        self.default_delivery_policy=self.SaleConfigSetting.create({})

        self.default_delivery_policy.execute()

    deftest_01_delivery_cost_from_pricelist(self):
        """Thistestaimstovalidatetheuseofapricelisttocomputethedeliverycostinthecasetheassociated
            productoftheshippingmethodisdefinedinthepricelist"""

        #Createpricelistwithacustompriceforthestandardshippingmethod
        my_pricelist=self.env['product.pricelist'].create({
            'name':'shipping_cost_change',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':5,
                'applied_on':'0_product_variant',
                'product_id':self.normal_delivery.product_id.id,
            })],
        })

        #CreatesalesorderwithNormalDeliveryCharges
        sale_pricelist_based_delivery_charges=self.SaleOrder.create({
            'partner_id':self.partner_18.id,
            'pricelist_id':my_pricelist.id,
            'order_line':[(0,0,{
                'name':'PCAssamble+2GBRAM',
                'product_id':self.product_4.id,
                'product_uom_qty':1,
                'product_uom':self.product_uom_unit.id,
                'price_unit':750.00,
            })],
        })

        #AddofdeliverycostinSalesorder
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id':sale_pricelist_based_delivery_charges.id,
            'default_carrier_id':self.normal_delivery.id
        }))
        self.assertEqual(delivery_wizard.delivery_price,5.0,"Deliverycostdoesnotcorrespondto5.0inwizard")
        delivery_wizard.save().button_confirm()

        line=self.SaleOrderLine.search([('order_id','=',sale_pricelist_based_delivery_charges.id),
                                          ('product_id','=',self.normal_delivery.product_id.id)])
        self.assertEqual(len(line),1,"Deliverycosthasn'tbeenaddedtoSO")
        self.assertEqual(line.price_subtotal,5.0,"Deliverycostdoesnotcorrespondto5.0")

    deftest_02_delivery_cost_from_different_currency(self):
        """Thistestaimstovalidatetheuseofapricelistusingadifferentcurrencytocomputethedeliverycostin
            thecasetheassociatedproductoftheshippingmethodisdefinedinthepricelist"""

        #Createpricelistwithacustompriceforthestandardshippingmethod
        my_pricelist=self.env['product.pricelist'].create({
            'name':'shipping_cost_change',
            'item_ids':[(0,0,{
                'compute_price':'fixed',
                'fixed_price':5,
                'applied_on':'0_product_variant',
                'product_id':self.normal_delivery.product_id.id,
            })],
            'currency_id':self.env.ref('base.EUR').id,
        })

        #CreatesalesorderwithNormalDeliveryCharges
        sale_pricelist_based_delivery_charges=self.SaleOrder.create({
            'partner_id':self.partner_18.id,
            'pricelist_id':my_pricelist.id,
            'order_line':[(0,0,{
                'name':'PCAssamble+2GBRAM',
                'product_id':self.product_4.id,
                'product_uom_qty':1,
                'product_uom':self.product_uom_unit.id,
                'price_unit':750.00,
            })],
        })

        #AddofdeliverycostinSalesorder
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context({
            'default_order_id':sale_pricelist_based_delivery_charges.id,
            'default_carrier_id':self.normal_delivery.id
        }))
        self.assertEqual(delivery_wizard.delivery_price,5.0,"Deliverycostdoesnotcorrespondto5.0inwizard")
        delivery_wizard.save().button_confirm()

        line=self.SaleOrderLine.search([('order_id','=',sale_pricelist_based_delivery_charges.id),
                                          ('product_id','=',self.normal_delivery.product_id.id)])
        self.assertEqual(len(line),1,"Deliverycosthasn'tbeenaddedtoSO")
        self.assertEqual(line.price_subtotal,5.0,"Deliverycostdoesnotcorrespondto5.0")

    deftest_01_taxes_on_delivery_cost(self):

        #Creatingtaxesandfiscalposition

        tax_price_include=self.env['account.tax'].create({
            'name':'10%inc',
            'type_tax_use':'sale',
            'amount_type':'percent',
            'amount':10,
            'price_include':True,
            'include_base_amount':True,
        })
        tax_price_exclude=self.env['account.tax'].create({
            'name':'15%exc',
            'type_tax_use':'sale',
            'amount_type':'percent',
            'amount':15,
        })

        fiscal_position=self.env['account.fiscal.position'].create({
            'name':'fiscal_pos_a',
            'tax_ids':[
                (0,None,{
                    'tax_src_id':tax_price_include.id,
                    'tax_dest_id':tax_price_exclude.id,
                }),
            ],
        })

        #Settingtaxondeliveryproduct
        self.normal_delivery.product_id.taxes_id=tax_price_include

        #Createsalesorder
        order_form=Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id=self.partner_18
        order_form.pricelist_id=self.pricelist
        order_form.fiscal_position_id=fiscal_position

        #Tryaddingdeliveryproductasanormalproduct
        withorder_form.order_line.new()asline:
            line.product_id=self.normal_delivery.product_id
            line.product_uom_qty=1.0
            line.product_uom=self.product_uom_unit
        sale_order=order_form.save()

        self.assertRecordValues(sale_order.order_line,[{'price_subtotal':9.09,'price_total':10.45}])

        #Nowtryingtoaddthedeliverylineusingthedeliverywizard,theresultsshouldbethesameasbefore
        delivery_wizard=Form(self.env['choose.delivery.carrier'].with_context(default_order_id=sale_order.id,
                          default_carrier_id=self.normal_delivery.id))
        choose_delivery_carrier=delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

        line=self.SaleOrderLine.search([
            ('order_id','=',sale_order.id),
            ('product_id','=',self.normal_delivery.product_id.id),
            ('is_delivery','=',True)
        ])

        self.assertRecordValues(line,[{'price_subtotal':9.09,'price_total':10.45}])

    deftest_add_carrier_on_picking(self):
        """
        AuserconfirmsaSO,thenaddsacarrieronthepicking.Theinvoicing
        policyofthecarrierissetto"RealCost".Hethenconfirmsthe
        picking:alinewiththecarriercostshouldbeaddedtotheSO
        """
        self.normal_delivery.invoice_policy='real'

        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.partner_4
        withso_form.order_line.new()asline:
            line.product_id=self.product_2
        so=so_form.save()
        so.action_confirm()

        picking=so.picking_ids
        picking.carrier_id=self.normal_delivery
        picking.move_lines.quantity_done=1
        picking.button_validate()

        so.order_line.invalidate_cache(ids=so.order_line.ids)

        self.assertEqual(picking.state,'done')
        self.assertRecordValues(so.order_line,[
            {'product_id':self.product_2.id,'is_delivery':False,'product_uom_qty':1,'qty_delivered':1},
            {'product_id':self.normal_delivery.product_id.id,'is_delivery':True,'product_uom_qty':1,'qty_delivered':0},
        ])

    deftest_estimated_weight(self):
        """
        TestthatnegativeqtySOlinesarenotincludedintheestimatedweightcalculation
        ofdeliverycarriers(sinceit'susedwhencalculatingtheirrates).
        """
        sale_order=self.SaleOrder.create({
            'partner_id':self.partner_18.id,
            'name':'SO-negqty',
            'order_line':[
                (0,0,{
                    'product_id':self.product_4.id,
                    'product_uom_qty':1,
                    'product_uom':self.product_uom_unit.id,
                }),
                (0,0,{
                    'product_id':self.product_2.id,
                    'product_uom_qty':-1,
                    'product_uom':self.product_uom_unit.id,
                })],
        })
        shipping_weight=sale_order._get_estimated_weight()
        self.assertEqual(shipping_weight,self.product_4.weight,"Onlypositivequantityproducts'weightsshouldbeincludedinestimatedweight")
