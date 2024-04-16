#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged,Form


@tagged('post_install','-at_install')
classTestRepair(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #Partners
        cls.res_partner_1=cls.env['res.partner'].create({'name':'WoodCorner'})
        cls.res_partner_address_1=cls.env['res.partner'].create({'name':'WillieBurke','parent_id':cls.res_partner_1.id})
        cls.res_partner_12=cls.env['res.partner'].create({'name':'Partner12'})

        #Products
        cls.product_product_3=cls.env['product.product'].create({'name':'DeskCombination'})
        cls.product_product_11=cls.env['product.product'].create({'name':'ConferenceChair'})
        cls.product_product_5=cls.env['product.product'].create({'name':'Product5'})
        cls.product_product_6=cls.env['product.product'].create({'name':'LargeCabinet'})
        cls.product_product_12=cls.env['product.product'].create({'name':'OfficeChairBlack'})
        cls.product_product_13=cls.env['product.product'].create({'name':'CornerDeskLeftSit'})
        cls.product_product_2=cls.env['product.product'].create({'name':'VirtualHomeStaging'})
        cls.product_service_order_repair=cls.env['product.product'].create({
            'name':'RepairServices',
            'type':'service',
        })

        #Location
        cls.stock_warehouse=cls.env['stock.warehouse'].search([('company_id','=',cls.env.company.id)],limit=1)
        cls.stock_location_14=cls.env['stock.location'].create({
            'name':'Shelf2',
            'location_id':cls.stock_warehouse.lot_stock_id.id,
        })

        #RepairOrders
        cls.repair1=cls.env['repair.order'].create({
            'address_id':cls.res_partner_address_1.id,
            'guarantee_limit':'2019-01-01',
            'invoice_method':'none',
            'user_id':False,
            'product_id':cls.product_product_3.id,
            'product_uom':cls.env.ref('uom.product_uom_unit').id,
            'partner_invoice_id':cls.res_partner_address_1.id,
            'location_id':cls.stock_warehouse.lot_stock_id.id,
            'operations':[
                (0,0,{
                    'location_dest_id':cls.product_product_11.property_stock_production.id,
                    'location_id':cls.stock_warehouse.lot_stock_id.id,
                    'name':cls.product_product_11.get_product_multiline_description_sale(),
                    'product_id':cls.product_product_11.id,
                    'product_uom':cls.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty':1.0,
                    'price_unit':50.0,
                    'state':'draft',
                    'type':'add',
                    'company_id':cls.env.company.id,
                })
            ],
            'fees_lines':[
                (0,0,{
                    'name':cls.product_service_order_repair.get_product_multiline_description_sale(),
                    'product_id':cls.product_service_order_repair.id,
                    'product_uom_qty':1.0,
                    'product_uom':cls.env.ref('uom.product_uom_unit').id,
                    'price_unit':50.0,
                    'company_id':cls.env.company.id,
                })
            ],
            'partner_id':cls.res_partner_12.id,
        })

        cls.repair0=cls.env['repair.order'].create({
            'product_id':cls.product_product_5.id,
            'product_uom':cls.env.ref('uom.product_uom_unit').id,
            'address_id':cls.res_partner_address_1.id,
            'guarantee_limit':'2019-01-01',
            'invoice_method':'after_repair',
            'user_id':False,
            'partner_invoice_id':cls.res_partner_address_1.id,
            'location_id':cls.stock_warehouse.lot_stock_id.id,
            'operations':[
                (0,0,{
                    'location_dest_id':cls.product_product_12.property_stock_production.id,
                    'location_id':cls.stock_warehouse.lot_stock_id.id,
                    'name':cls.product_product_12.get_product_multiline_description_sale(),
                    'price_unit':50.0,
                    'product_id':cls.product_product_12.id,
                    'product_uom':cls.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty':1.0,
                    'state':'draft',
                    'type':'add',
                    'company_id':cls.env.company.id,
                })
            ],
            'fees_lines':[
                (0,0,{
                    'name':cls.product_service_order_repair.get_product_multiline_description_sale(),
                    'product_id':cls.product_service_order_repair.id,
                    'product_uom_qty':1.0,
                    'product_uom':cls.env.ref('uom.product_uom_unit').id,
                    'price_unit':50.0,
                    'company_id':cls.env.company.id,
                })
            ],
            'partner_id':cls.res_partner_12.id,
        })

        cls.repair2=cls.env['repair.order'].create({
            'product_id':cls.product_product_6.id,
            'product_uom':cls.env.ref('uom.product_uom_unit').id,
            'address_id':cls.res_partner_address_1.id,
            'guarantee_limit':'2019-01-01',
            'invoice_method':'b4repair',
            'user_id':False,
            'partner_invoice_id':cls.res_partner_address_1.id,
            'location_id':cls.stock_location_14.id,
            'operations':[
                (0,0,{
                    'location_dest_id':cls.product_product_13.property_stock_production.id,
                    'location_id':cls.stock_warehouse.lot_stock_id.id,
                    'name':cls.product_product_13.get_product_multiline_description_sale(),
                    'price_unit':50.0,
                    'product_id':cls.product_product_13.id,
                    'product_uom':cls.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty':1.0,
                    'state':'draft',
                    'type':'add',
                    'company_id':cls.env.company.id,
                })
            ],
            'fees_lines':[
                (0,0,{
                    'name':cls.product_service_order_repair.get_product_multiline_description_sale(),
                    'product_id':cls.product_service_order_repair.id,
                    'product_uom_qty':1.0,
                    'product_uom':cls.env.ref('uom.product_uom_unit').id,
                    'price_unit':50.0,
                    'company_id':cls.env.company.id,
                })
            ],
            'partner_id':cls.res_partner_12.id,
        })

        cls.env.user.groups_id|=cls.env.ref('stock.group_stock_user')

    def_create_simple_repair_order(self,invoice_method):
        product_to_repair=self.product_product_5
        partner=self.res_partner_address_1
        returnself.env['repair.order'].create({
            'product_id':product_to_repair.id,
            'product_uom':product_to_repair.uom_id.id,
            'address_id':partner.id,
            'guarantee_limit':'2019-01-01',
            'invoice_method':invoice_method,
            'partner_invoice_id':partner.id,
            'location_id':self.stock_warehouse.lot_stock_id.id,
            'partner_id':self.res_partner_12.id
        })

    def_create_simple_operation(self,repair_id=False,qty=0.0,price_unit=0.0):
        product_to_add=self.product_product_5
        returnself.env['repair.line'].create({
            'name':'AddTheproduct',
            'type':'add',
            'product_id':product_to_add.id,
            'product_uom_qty':qty,
            'product_uom':product_to_add.uom_id.id,
            'price_unit':price_unit,
            'repair_id':repair_id,
            'location_id':self.stock_warehouse.lot_stock_id.id,
            'location_dest_id':product_to_add.property_stock_production.id,
            'company_id':self.env.company.id,
        })

    def_create_simple_fee(self,repair_id=False,qty=0.0,price_unit=0.0):
        product_service=self.product_product_2
        returnself.env['repair.fee'].create({
            'name':'PCAssemble+Custom(PConDemand)',
            'product_id':product_service.id,
            'product_uom_qty':qty,
            'product_uom':product_service.uom_id.id,
            'price_unit':price_unit,
            'repair_id':repair_id,
            'company_id':self.env.company.id,
        })

    deftest_00_repair_afterinv(self):
        repair=self._create_simple_repair_order('after_repair')
        self._create_simple_operation(repair_id=repair.id,qty=1.0,price_unit=50.0)
        #IconfirmRepairordertakingInvoiceMethod'AfterRepair'.
        repair.action_repair_confirm()

        #Icheckthestateisin"Confirmed".
        self.assertEqual(repair.state,"confirmed",'Repairordershouldbein"Confirmed"state.')
        repair.action_repair_start()

        #Icheckthestateisin"UnderRepair".
        self.assertEqual(repair.state,"under_repair",'Repairordershouldbein"Under_repair"state.')

        #RepairingprocessforproductisinDonestateandIendRepairprocessbyclickingon"EndRepair"button.
        repair.action_repair_end()

        #IdefineInvoiceMethod'AfterRepair'optioninthisRepairorder.soIcreateinvoicebyclickingon"MakeInvoice"wizard.
        make_invoice=self.env['repair.order.make_invoice'].create({
            'group':True})
        #Iclickon"CreateInvoice"buttonofthiswizardtomakeinvoice.
        context={
            "active_model":'repair_order',
            "active_ids":[repair.id],
            "active_id":repair.id
        }
        make_invoice.with_context(context).make_invoices()

        #IcheckthatinvoiceiscreatedforthisRepairorder.
        self.assertEqual(len(repair.invoice_id),1,"Noinvoiceexistsforthisrepairorder")
        self.assertEqual(len(repair.move_id.move_line_ids[0].consume_line_ids),1,"Consumelinesshouldbeset")

    deftest_01_repair_b4inv(self):
        repair=self._create_simple_repair_order('b4repair')
        #IconfirmRepairorderforInvoiceMethod'BeforeRepair'.
        repair.action_repair_confirm()

        #Iclickon"CreateInvoice"buttonofthiswizardtomakeinvoice.
        repair.action_repair_invoice_create()

        #IcheckthatinvoiceiscreatedforthisRepairorder.
        self.assertEqual(len(repair.invoice_id),1,"Noinvoiceexistsforthisrepairorder")

    deftest_02_repair_noneinv(self):
        repair=self._create_simple_repair_order('none')

        #Addanewfeeline
        self._create_simple_fee(repair_id=repair.id,qty=1.0,price_unit=12.0)

        self.assertEqual(repair.amount_total,12,"Amount_totalshouldbe12")
        #Addnewoperationline
        self._create_simple_operation(repair_id=repair.id,qty=1.0,price_unit=14.0)

        self.assertEqual(repair.amount_total,26,"Amount_totalshouldbe26")

        #IconfirmRepairorderforInvoiceMethod'NoInvoice'.
        repair.action_repair_confirm()

        #Istarttherepairingprocessbyclickingon"StartRepair"buttonforInvoiceMethod'NoInvoice'.
        repair.action_repair_start()

        #Icheckitsstatewhichisin"UnderRepair".
        self.assertEqual(repair.state,"under_repair",'Repairordershouldbein"Under_repair"state.')

        #RepairingprocessforproductisinDonestateandIendthisprocessbyclickingon"EndRepair"button.
        repair.action_repair_end()

        self.assertEqual(repair.move_id.location_id.id,self.stock_warehouse.lot_stock_id.id,
                         'Repairedproductwastakeninthewronglocation')
        self.assertEqual(repair.move_id.location_dest_id.id,self.stock_warehouse.lot_stock_id.id,
                         'Repairedproductwenttothewronglocation')
        self.assertEqual(repair.operations.move_id.location_id.id,self.stock_warehouse.lot_stock_id.id,
                         'Consumedproductwastakeninthewronglocation')
        self.assertEqual(repair.operations.move_id.location_dest_id.id,self.product_product_5.property_stock_production.id,
                         'Consumedproductwenttothewronglocation')

        #IdefineInvoiceMethod'NoInvoice'optioninthisrepairorder.
        #So,IcheckthatInvoicehasnotbeencreatedforthisrepairorder.
        self.assertNotEqual(len(repair.invoice_id),1,"Invoiceshouldnotexistforthisrepairorder")

    deftest_repair_state(self):
        repair=self._create_simple_repair_order('b4repair')
        repair.action_repair_confirm()
        repair.action_repair_invoice_create()
        repair.invoice_id.unlink()
        #Repairorderstateshouldbechangedto2binvoicedsothatnewinvoicecanbecreated
        self.assertEqual(repair.state,'2binvoiced','Repairordershouldbein2binvoicedstate,ifinvoiceisdeleted.')
        repair.action_repair_invoice_create()
        repair.action_repair_cancel()
        #Repairorderandlinkedinvoicebothshouldbecancelled.
        self.assertEqual(repair.state,'cancel','Repairordershouldbeincancelstate.')
        self.assertEqual(repair.invoice_id.state,'cancel','Invoiceshouldbeincancelstate.')
        repair.action_repair_cancel_draft()
        #Linkedinvoiceshouldbeunlinked
        self.assertEqual(len(repair.invoice_id),0,"Noinvoiceshouldbeexistsforthisrepairorder")

    deftest_03_repair_multicompany(self):
        """ThistestensuresthatthecorrecttaxesareselectedwhentheuserfillsintheROform"""

        company01=self.env.company
        company02=self.env['res.company'].create({
            'name':'SuperCompany',
        })

        tax01=self.env["account.tax"].create({
            "name":"C01Tax",
            "amount":"0.00",
            "company_id":company01.id
        })
        tax02=self.env["account.tax"].create({
            "name":"C02Tax",
            "amount":"0.00",
            "company_id":company02.id
        })

        super_product=self.env['product.template'].create({
            "name":"SuperProduct",
            "taxes_id":[(4,tax01.id),(4,tax02.id)],
        })
        super_variant=super_product.product_variant_id
        self.assertEqual(super_variant.taxes_id,tax01|tax02)

        ro_form=Form(self.env['repair.order'])
        ro_form.product_id=super_variant
        ro_form.partner_id=company01.partner_id
        withro_form.operations.new()asro_line:
            ro_line.product_id=super_variant
        withro_form.fees_lines.new()asfee_line:
            fee_line.product_id=super_variant
        repair_order=ro_form.save()

        #tax02shouldnotbepresentsinceitbelongstothesecondcompany.
        self.assertEqual(repair_order.operations.tax_id,tax01)
        self.assertEqual(repair_order.fees_lines.tax_id,tax01)
