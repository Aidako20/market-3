#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_commonimportValuationReconciliationTestCommon
fromflectra.testsimportcommon,Form
fromflectra.exceptionsimportUserError
fromflectra.toolsimportmute_logger,float_compare
fromflectra.addons.stock_account.tests.test_stockvaluationimport_create_accounting_data


#thesetestscreateaccountingentries,andthereforeneedachartofaccounts
@common.tagged('post_install','-at_install')
classTestSaleMrpFlow(ValuationReconciliationTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env.ref('stock.route_warehouse0_mto').active=True

        #Usefulmodels
        cls.StockMove=cls.env['stock.move']
        cls.UoM=cls.env['uom.uom']
        cls.MrpProduction=cls.env['mrp.production']
        cls.Inventory=cls.env['stock.inventory']
        cls.InventoryLine=cls.env['stock.inventory.line']
        cls.ProductCategory=cls.env['product.category']

        cls.categ_unit=cls.env.ref('uom.product_uom_categ_unit')
        cls.categ_kgm=cls.env.ref('uom.product_uom_categ_kgm')

        cls.uom_kg=cls.env['uom.uom'].search([('category_id','=',cls.categ_kgm.id),('uom_type','=','reference')],limit=1)
        cls.uom_kg.write({
            'name':'Test-KG',
            'rounding':0.000001})
        cls.uom_gm=cls.UoM.create({
            'name':'Test-G',
            'category_id':cls.categ_kgm.id,
            'uom_type':'smaller',
            'factor':1000.0,
            'rounding':0.001})
        cls.uom_unit=cls.env['uom.uom'].search([('category_id','=',cls.categ_unit.id),('uom_type','=','reference')],limit=1)
        cls.uom_unit.write({
            'name':'Test-Unit',
            'rounding':0.01})
        cls.uom_dozen=cls.UoM.create({
            'name':'Test-DozenA',
            'category_id':cls.categ_unit.id,
            'factor_inv':12,
            'uom_type':'bigger',
            'rounding':0.001})

        #Creatingallcomponents
        cls.component_a=cls._cls_create_product('CompA',cls.uom_unit)
        cls.component_b=cls._cls_create_product('CompB',cls.uom_unit)
        cls.component_c=cls._cls_create_product('CompC',cls.uom_unit)
        cls.component_d=cls._cls_create_product('CompD',cls.uom_unit)
        cls.component_e=cls._cls_create_product('CompE',cls.uom_unit)
        cls.component_f=cls._cls_create_product('CompF',cls.uom_unit)
        cls.component_g=cls._cls_create_product('CompG',cls.uom_unit)

        #Createakit'kit_1':
        #-----------------------
        #
        #kit_1--|-component_a  x2
        #        |-component_b  x1
        #        |-component_c  x3

        cls.kit_1=cls._cls_create_product('Kit1',cls.uom_unit)

        cls.bom_kit_1=cls.env['mrp.bom'].create({
            'product_tmpl_id':cls.kit_1.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine=cls.env['mrp.bom.line']
        BomLine.create({
            'product_id':cls.component_a.id,
            'product_qty':2.0,
            'bom_id':cls.bom_kit_1.id})
        BomLine.create({
            'product_id':cls.component_b.id,
            'product_qty':1.0,
            'bom_id':cls.bom_kit_1.id})
        BomLine.create({
            'product_id':cls.component_c.id,
            'product_qty':3.0,
            'bom_id':cls.bom_kit_1.id})

        #Createakit'kit_parent':
        #---------------------------
        #
        #kit_parent--|-kit_2x2--|-component_dx1
        #             |            |-kit_1x2-------|-component_a  x2
        #             |                               |-component_b  x1
        #             |                               |-component_c  x3
        #             |
        #             |-kit_3x1--|-component_fx1
        #             |            |-component_gx2
        #             |
        #             |-component_ex1

        #Creatingallkits
        cls.kit_2=cls._cls_create_product('Kit2',cls.uom_unit)
        cls.kit_3=cls._cls_create_product('kit3',cls.uom_unit)
        cls.kit_parent=cls._cls_create_product('KitParent',cls.uom_unit)

        #Linkingthekitsandthecomponentsviasome'phantom'BoMs
        bom_kit_2=cls.env['mrp.bom'].create({
            'product_tmpl_id':cls.kit_2.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine.create({
            'product_id':cls.component_d.id,
            'product_qty':1.0,
            'bom_id':bom_kit_2.id})
        BomLine.create({
            'product_id':cls.kit_1.id,
            'product_qty':2.0,
            'bom_id':bom_kit_2.id})

        bom_kit_parent=cls.env['mrp.bom'].create({
            'product_tmpl_id':cls.kit_parent.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine.create({
            'product_id':cls.component_e.id,
            'product_qty':1.0,
            'bom_id':bom_kit_parent.id})
        BomLine.create({
            'product_id':cls.kit_2.id,
            'product_qty':2.0,
            'bom_id':bom_kit_parent.id})

        bom_kit_3=cls.env['mrp.bom'].create({
            'product_tmpl_id':cls.kit_3.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine.create({
            'product_id':cls.component_f.id,
            'product_qty':1.0,
            'bom_id':bom_kit_3.id})
        BomLine.create({
            'product_id':cls.component_g.id,
            'product_qty':2.0,
            'bom_id':bom_kit_3.id})

        BomLine.create({
            'product_id':cls.kit_3.id,
            'product_qty':2.0,
            'bom_id':bom_kit_parent.id})

    @classmethod
    def_cls_create_product(cls,name,uom_id,routes=()):
        p=Form(cls.env['product.product'])
        p.name=name
        p.type='product'
        p.uom_id=uom_id
        p.uom_po_id=uom_id
        p.route_ids.clear()
        forrinroutes:
            p.route_ids.add(r)
        returnp.save()

    def_create_product(self,name,uom_id,routes=()):
        p=Form(self.env['product.product'])
        p.name=name
        p.type='product'
        p.uom_id=uom_id
        p.uom_po_id=uom_id
        p.route_ids.clear()
        forrinroutes:
            p.route_ids.add(r)
        returnp.save()

        #Helpertoprocessquantitiesbasedonadictfollowingthisstructure:
        #
        #qty_to_process={
        #    product_id:qty
        #}

    def_process_quantities(self,moves,quantities_to_process):
        """Helpertoprocessquantitiesbasedonadictfollowingthisstructure:
            qty_to_process={
                product_id:qty
            }
        """
        moves_to_process=moves.filtered(lambdam:m.product_idinquantities_to_process.keys())
        formoveinmoves_to_process:
            move.write({'quantity_done':quantities_to_process[move.product_id]})

    def_assert_quantities(self,moves,quantities_to_process):
        """Helpertocheckexpectedquantitiesbasedonadictfollowingthisstructure:
            qty_to_process={
                product_id:qty
                ...
            }
        """
        moves_to_process=moves.filtered(lambdam:m.product_idinquantities_to_process.keys())
        formoveinmoves_to_process:
            self.assertEqual(move.product_uom_qty,quantities_to_process[move.product_id])

    def_create_move_quantities(self,qty_to_process,components,warehouse):
        """Helpertocreatesmovesinordertoupdatethequantitiesofcomponents
        onaspecificwarehouse.Thisensurethatallcomputefieldsaretriggered.
        Thestructureofqty_to_processshouldbethefollowing:

         qty_to_process={
            component:(qty,uom),
            ...
        }
        """
        forcompincomponents:
            f=Form(self.env['stock.move'])
            f.name='TestReceiptComponents'
            f.location_id=self.env.ref('stock.stock_location_suppliers')
            f.location_dest_id=warehouse.lot_stock_id
            f.product_id=comp
            f.product_uom=qty_to_process[comp][1]
            f.product_uom_qty=qty_to_process[comp][0]
            move=f.save()
            move._action_confirm()
            move._action_assign()
            move_line=move.move_line_ids[0]
            move_line.qty_done=qty_to_process[comp][0]
            move._action_done()

    deftest_00_sale_mrp_flow(self):
        """Testsaletomrpflowwithdiffrentunitofmeasure."""


        #CreateproductA,B,C,D.
        #--------------------------
        route_manufacture=self.company_data['default_warehouse'].manufacture_pull_id.route_id
        route_mto=self.company_data['default_warehouse'].mto_pull_id.route_id
        product_a=self._create_product('ProductA',self.uom_unit,routes=[route_manufacture,route_mto])
        product_c=self._create_product('ProductC',self.uom_kg)
        product_b=self._create_product('ProductB',self.uom_dozen,routes=[route_manufacture,route_mto])
        product_d=self._create_product('ProductD',self.uom_unit,routes=[route_manufacture,route_mto])

        #------------------------------------------------------------------------------------------
        #BillofmaterialsforproductA,B,D.
        #------------------------------------------------------------------------------------------

        #BillofmaterialsforProductA.
        withForm(self.env['mrp.bom'])asf:
            f.product_tmpl_id=product_a.product_tmpl_id
            f.product_qty=2
            f.product_uom_id=self.uom_dozen
            withf.bom_line_ids.new()asline:
                line.product_id=product_b
                line.product_qty=3
                line.product_uom_id=self.uom_unit
            withf.bom_line_ids.new()asline:
                line.product_id=product_c
                line.product_qty=300.5
                line.product_uom_id=self.uom_gm
            withf.bom_line_ids.new()asline:
                line.product_id=product_d
                line.product_qty=4
                line.product_uom_id=self.uom_unit

        #BillofmaterialsforProductB.
        withForm(self.env['mrp.bom'])asf:
            f.product_tmpl_id=product_b.product_tmpl_id
            f.product_qty=1
            f.product_uom_id=self.uom_unit
            f.type='phantom'
            withf.bom_line_ids.new()asline:
                line.product_id=product_c
                line.product_qty=0.400
                line.product_uom_id=self.uom_kg

        #BillofmaterialsforProductD.
        withForm(self.env['mrp.bom'])asf:
            f.product_tmpl_id=product_d.product_tmpl_id
            f.product_qty=1
            f.product_uom_id=self.uom_unit
            withf.bom_line_ids.new()asline:
                line.product_id=product_c
                line.product_qty=1
                line.product_uom_id=self.uom_kg

        #----------------------------------------
        #Createsalesorderof10DozenproductA.
        #----------------------------------------

        order_form=Form(self.env['sale.order'])
        order_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        withorder_form.order_line.new()asline:
            line.product_id=product_a
            line.product_uom=self.uom_dozen
            line.product_uom_qty=10
        order=order_form.save()
        order.action_confirm()

        #Verifybuttonsareworkingasexpected
        self.assertEqual(order.mrp_production_count,1,"Usershouldseetheclosestmanufactureorderinthesmartbutton")

        #===============================================================================
        # Salesorderof10DozenproductAshouldcreateproductionorder
        # like..
        #===============================================================================
        #   ProductA 10Dozen.
        #       ProductC 6kg
        #               AsproductBphantominbomA,productAwillconsumeproductC
        #               ================================================================
        #               For1unitproductBitwillconsume400gm
        #               thenfor15unit(ProductB3unitper2DozenproductA)
        #               productBitwillconsume[6kg]productC)
        #               ProductAwillconsume6kgproductC.
        #
        #               [15*400gm(6kgproductC)]=6kgproductC
        #
        #       ProductC 1502.5gm.
        #               [
        #                 For2DozenproductAwillconsume300.5gmproductC
        #                 thenfor10DozenproductAwillconsume1502.5gmproductC.
        #               ]
        #
        #       productD 20Unit.
        #               [
        #                 For2dozenproductAwillconsume4unitproductD
        #                 thenfor10DozenproductAwillconsume20unitofproductD.
        #               ]
        #--------------------------------------------------------------------------------

        #<><><><><><><><><><><><><><><><><><><><>
        #CheckmanufacturingorderforproductA.
        #<><><><><><><><><><><><><><><><><><><><>

        #Checkquantity,unitofmeasureandstateofmanufacturingorder.
        #-----------------------------------------------------------------
        self.env['procurement.group'].run_scheduler()
        mnf_product_a=self.env['mrp.production'].search([('product_id','=',product_a.id)])

        self.assertTrue(mnf_product_a,'Manufacturingordernotcreated.')
        self.assertEqual(mnf_product_a.product_qty,120,'Wrongproductquantityinmanufacturingorder.')
        self.assertEqual(mnf_product_a.product_uom_id,self.uom_unit,'Wrongunitofmeasureinmanufacturingorder.')
        self.assertEqual(mnf_product_a.state,'confirmed','Manufacturingordershouldbeconfirmed.')

        #------------------------------------------------------------------------------------------
        #Check'Toconsumeline'forproductionorderofproductA.
        #------------------------------------------------------------------------------------------

        #Check'Toconsumeline'withproductcanduomkg.
        #-------------------------------------------------

        moves=self.StockMove.search([
            ('raw_material_production_id','=',mnf_product_a.id),
            ('product_id','=',product_c.id),
            ('product_uom','=',self.uom_kg.id)])

        #Checktotalconsumelinewithproductcanduomkg.
        self.assertEqual(len(moves),1,'Productionmovelinesarenotgeneratedproper.')
        list_qty={move.product_uom_qtyformoveinmoves}
        self.assertEqual(list_qty,{6.0},"Wrongproductquantityin'Toconsumeline'ofmanufacturingorder.")
        #Checkstateofconsumelinewithproductcanduomkg.
        formoveinmoves:
            self.assertEqual(move.state,'confirmed',"Wrongstatein'Toconsumeline'ofmanufacturingorder.")

        #Check'Toconsumeline'withproductcanduomgm.
        #---------------------------------------------------

        move=self.StockMove.search([
            ('raw_material_production_id','=',mnf_product_a.id),
            ('product_id','=',product_c.id),
            ('product_uom','=',self.uom_gm.id)])

        #Checktotalconsumelineofproductcwithgm.
        self.assertEqual(len(move),1,'Productionmovelinesarenotgeneratedproper.')
        #Checkquantityshouldbewith1502.5(2DozenproductAconsume300.5gmthen10Dozen(300.5*(10/2)).
        self.assertEqual(move.product_uom_qty,1502.5,"Wrongproductquantityin'Toconsumeline'ofmanufacturingorder.")
        #Checkstateofconsumelinewithproductcwithanduomgm.
        self.assertEqual(move.state,'confirmed',"Wrongstatein'Toconsumeline'ofmanufacturingorder.")

        #Check'Toconsumeline'withproductD.
        #---------------------------------------

        move=self.StockMove.search([
            ('raw_material_production_id','=',mnf_product_a.id),
            ('product_id','=',product_d.id)])

        #ChecktotalconsumelinewithproductD.
        self.assertEqual(len(move),1,'Productionlinesarenotgeneratedproper.')

        #<><><><><><><><><><><><><><><><><><><><><><>
        #ManufacturingorderforproductD(20unit).
        #<><><><><><><><><><><><><><><><><><><><><><>

        #FPTodo:findabetterwaytolookfortheproductionorder
        mnf_product_d=self.MrpProduction.search([('product_id','=',product_d.id)],order='iddesc',limit=1)
        #CheckstateofproductionorderD.
        self.assertEqual(mnf_product_d.state,'confirmed','Manufacturingordershouldbeconfirmed.')

        #Check'Toconsumeline'state,quantity,uomofproductionorder(productD).
        #-----------------------------------------------------------------------------

        move=self.StockMove.search([('raw_material_production_id','=',mnf_product_d.id),('product_id','=',product_c.id)])
        self.assertEqual(move.product_uom_qty,20,"Wrongproductquantityin'Toconsumeline'ofmanufacturingorder.")
        self.assertEqual(move.product_uom.id,self.uom_kg.id,"Wrongunitofmeasurein'Toconsumeline'ofmanufacturingorder.")
        self.assertEqual(move.state,'confirmed',"Wrongstatein'Toconsumeline'ofmanufacturingorder.")

        #-------------------------------
        #Createinventoryforproductc.
        #-------------------------------
        #Need20kgproductctoproduce20unitproductD.
        #--------------------------------------------------

        inventory=self.Inventory.create({
            'name':'InventoryProductKG',
            'product_ids':[(4,product_c.id)]})

        inventory.action_start()
        self.assertFalse(inventory.line_ids,"Inventorylineshouldnotcreated.")
        self.InventoryLine.create({
            'inventory_id':inventory.id,
            'product_id':product_c.id,
            'product_uom_id':self.uom_kg.id,
            'product_qty':20,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id})
        inventory.action_validate()

        #--------------------------------------------------
        #AssignproductctomanufacturingorderofproductD.
        #--------------------------------------------------

        mnf_product_d.action_assign()
        self.assertEqual(mnf_product_d.reservation_state,'assigned','Availabilityshouldbeassigned')
        self.assertEqual(move.state,'assigned',"Wrongstatein'Toconsumeline'ofmanufacturingorder.")

        #------------------
        #produceproductD.
        #------------------

        mo_form=Form(mnf_product_d)
        mo_form.qty_producing=20
        mnf_product_d=mo_form.save()
        mnf_product_d._post_inventory()

        #Checkstateofmanufacturingorder.
        self.assertEqual(mnf_product_d.state,'done','Manufacturingordershouldstillbeinprogressstate.')
        #CheckavailablequantityofproductD.
        self.assertEqual(product_d.qty_available,20,'WrongquantityavailableofproductD.')

        #-----------------------------------------------------------------
        #CheckproductDassignedornottoproductionorderofproductA.
        #-----------------------------------------------------------------

        self.assertEqual(mnf_product_a.state,'confirmed','Manufacturingordershouldbeconfirmed.')
        move=self.StockMove.search([('raw_material_production_id','=',mnf_product_a.id),('product_id','=',product_d.id)])
        self.assertEqual(move.state,'assigned',"Wrongstatein'Toconsumeline'ofmanufacturingorder.")

        #CreateinventoryforproductC.
        #------------------------------
        #NeedproductC(20kg+6kg+1502.5gm=27.5025kg)
        #-------------------------------------------------------
        inventory=self.Inventory.create({
            'name':'InventoryProductCKG',
            'product_ids':[(4,product_c.id)]})

        inventory.action_start()
        self.assertFalse(inventory.line_ids,"Inventorylineshouldnotcreated.")
        self.InventoryLine.create({
            'inventory_id':inventory.id,
            'product_id':product_c.id,
            'product_uom_id':self.uom_kg.id,
            'product_qty':27.5025,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id})
        inventory.action_validate()

        #AssignproducttomanufacturingorderofproductA.
        #---------------------------------------------------

        mnf_product_a.action_assign()
        self.assertEqual(mnf_product_a.reservation_state,'assigned','Manufacturingorderinventorystateshouldbeavailable.')
        moves=self.StockMove.search([('raw_material_production_id','=',mnf_product_a.id),('product_id','=',product_c.id)])

        #Checkproductcmovelinestate.
        formoveinmoves:
            self.assertEqual(move.state,'assigned',"Wrongstatein'Toconsumeline'ofmanufacturingorder.")

        #ProduceproductA.
        #------------------

        mo_form=Form(mnf_product_a)
        mo_form.qty_producing=mo_form.product_qty
        mnf_product_a=mo_form.save()
        mnf_product_a._post_inventory()
        #CheckstateofmanufacturingorderproductA.
        self.assertEqual(mnf_product_a.state,'done','Manufacturingordershouldstillbeintheprogressstate.')
        #CheckproductAavaialblequantityshouldbe120.
        self.assertEqual(product_a.qty_available,120,'WrongquantityavailableofproductA.')

    deftest_01_sale_mrp_delivery_kit(self):
        """TestdeliveredquantityonSObasedondeliveredquantityinpickings."""
        #intialso
        product=self.env['product.product'].create({
            'name':'TableKit',
            'type':'consu',
            'invoice_policy':'delivery',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        #RemovetheMTOrouteaspurchaseisnotinstalledandsincetheprocurementremovaltheexceptionisdirectlyraised
        product.write({'route_ids':[(6,0,[self.company_data['default_warehouse'].manufacture_pull_id.route_id.id])]})

        product_wood_panel=self.env['product.product'].create({
            'name':'WoodPanel',
            'type':'product',
        })
        product_desk_bolt=self.env['product.product'].create({
            'name':'Bolt',
            'type':'product',
        })
        self.env['mrp.bom'].create({
            'product_tmpl_id':product.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'sequence':2,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{
                    'product_id':product_wood_panel.id,
                    'product_qty':1,
                    'product_uom_id':self.env.ref('uom.product_uom_unit').id,
                }),(0,0,{
                    'product_id':product_desk_bolt.id,
                    'product_qty':4,
                    'product_uom_id':self.env.ref('uom.product_uom_unit').id,
                })
            ]
        })

        partner=self.env['res.partner'].create({'name':'MyTestPartner'})
        #if`delivery`moduleisinstalled,adefaultpropertyissetforthecarriertouse
        #HoweverthiswillleadtoanextralineontheSO(thedeliveryline),whichwillforce
        #theSOtohaveadifferentflow(and`invoice_state`value)
        if'property_delivery_carrier_id'inpartner:
            partner.property_delivery_carrier_id=False

        f=Form(self.env['sale.order'])
        f.partner_id=partner
        withf.order_line.new()asline:
            line.product_id=product
            line.product_uom_qty=5
        so=f.save()

        #confirmourstandardso,checkthepicking
        so.action_confirm()
        self.assertTrue(so.picking_ids,'SaleMRP:nopickingcreatedfor"invoiceondelivery"storableproducts')

        #invoiceinondelivery,nothingshouldbeinvoiced
        withself.assertRaises(UserError):
            so._create_invoices()
        self.assertEqual(so.invoice_status,'no','SaleMRP:soinvoice_statusshouldbe"nothingtoinvoice"afterinvoicing')

        #deliverpartially(1ofeachinsteadof5),checktheso'sinvoice_statusanddeliveredquantities
        pick=so.picking_ids
        pick.move_lines.write({'quantity_done':1})
        wiz_act=pick.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()
        self.assertEqual(so.invoice_status,'no','SaleMRP:soinvoice_statusshouldbe"no"afterpartialdeliveryofakit')
        del_qty=sum(sol.qty_deliveredforsolinso.order_line)
        self.assertEqual(del_qty,0.0,'SaleMRP:deliveredquantityshouldbezeroafterpartialdeliveryofakit')
        #deliverremainingproducts,checktheso'sinvoice_statusanddeliveredquantities
        self.assertEqual(len(so.picking_ids),2,'SaleMRP:numberofpickingsshouldbe2')
        pick_2=so.picking_ids.filtered('backorder_id')
        formoveinpick_2.move_lines:
            ifmove.product_id.id==product_desk_bolt.id:
                move.write({'quantity_done':19})
            else:
                move.write({'quantity_done':4})
        pick_2.button_validate()

        del_qty=sum(sol.qty_deliveredforsolinso.order_line)
        self.assertEqual(del_qty,5.0,'SaleMRP:deliveredquantityshouldbe5.0aftercompletedeliveryofakit')
        self.assertEqual(so.invoice_status,'toinvoice','SaleMRP:soinvoice_statusshouldbe"toinvoice"aftercompletedeliveryofakit')

    deftest_02_sale_mrp_anglo_saxon(self):
        """Testthepriceunitofakit"""
        #Thistestwillcheckthatthecorrectjournalentriesarecreatedwhenastockableproductinrealtimevaluation
        #andinfifocostmethodissoldinacompanyusinganglo-saxon.
        #Forthistest,let'sconsideraproductcategorycalledTestcategoryinreal-timevaluationandrealpricecostingmethod
        #Let's alsoconsiderafinishedproductwithabomwithtwocomponents:component1(cost=20)andcomponent2(cost=10)
        #TheseproductsareintheTestcategory
        #Thebomconsistsof2component1and1component2
        #Theinvoicepolicyofthefinishedproductisbasedondeliveredquantities
        self.env.company.currency_id=self.env.ref('base.USD')
        self.uom_unit=self.UoM.create({
            'name':'Test-Unit',
            'category_id':self.categ_unit.id,
            'factor':1,
            'uom_type':'bigger',
            'rounding':1.0})
        self.company=self.company_data['company']
        self.company.anglo_saxon_accounting=True
        self.partner=self.env['res.partner'].create({'name':'MyTestPartner'})
        self.category=self.env.ref('product.product_category_1').copy({'name':'Testcategory','property_valuation':'real_time','property_cost_method':'fifo'})
        account_type=self.env['account.account.type'].create({'name':'RCVtype','type':'other','internal_group':'asset'})
        self.account_receiv=self.env['account.account'].create({'name':'Receivable','code':'RCV00','user_type_id':account_type.id,'reconcile':True})
        account_expense=self.env['account.account'].create({'name':'Expense','code':'EXP00','user_type_id':account_type.id,'reconcile':True})
        account_output=self.env['account.account'].create({'name':'Output','code':'OUT00','user_type_id':account_type.id,'reconcile':True})
        account_valuation=self.env['account.account'].create({'name':'Valuation','code':'STV00','user_type_id':account_type.id,'reconcile':True})
        self.partner.property_account_receivable_id=self.account_receiv
        self.category.property_account_income_categ_id=self.account_receiv
        self.category.property_account_expense_categ_id=account_expense
        self.category.property_stock_account_input_categ_id=self.account_receiv
        self.category.property_stock_account_output_categ_id=account_output
        self.category.property_stock_valuation_account_id=account_valuation
        self.category.property_stock_journal=self.env['account.journal'].create({'name':'Stockjournal','type':'sale','code':'STK00'})

        Product=self.env['product.product']
        self.finished_product=Product.create({
                'name':'Finishedproduct',
                'type':'product',
                'uom_id':self.uom_unit.id,
                'invoice_policy':'delivery',
                'categ_id':self.category.id})
        self.component1=Product.create({
                'name':'Component1',
                'type':'product',
                'uom_id':self.uom_unit.id,
                'categ_id':self.category.id,
                'standard_price':20})
        self.component2=Product.create({
                'name':'Component2',
                'type':'product',
                'uom_id':self.uom_unit.id,
                'categ_id':self.category.id,
                'standard_price':10})

        #Createquantswithsudotoavoid:
        #"Youarenotallowedtocreate'Quants'(stock.quant)records.Nogroupcurrentlyallowsthisoperation."
        self.env['stock.quant'].sudo().create({
            'product_id':self.component1.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'quantity':6.0,
        })
        self.env['stock.quant'].sudo().create({
            'product_id':self.component2.id,
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'quantity':3.0,
        })
        self.bom=self.env['mrp.bom'].create({
                'product_tmpl_id':self.finished_product.product_tmpl_id.id,
                'product_qty':1.0,
                'type':'phantom'})
        BomLine=self.env['mrp.bom.line']
        BomLine.create({
                'product_id':self.component1.id,
                'product_qty':2.0,
                'bom_id':self.bom.id})
        BomLine.create({
                'product_id':self.component2.id,
                'product_qty':1.0,
                'bom_id':self.bom.id})

        #CreateaSOforaspecificpartnerforthreeunitsofthefinishedproduct
        so_vals={
            'partner_id':self.partner.id,
            'partner_invoice_id':self.partner.id,
            'partner_shipping_id':self.partner.id,
            'order_line':[(0,0,{
                'name':self.finished_product.name,
                'product_id':self.finished_product.id,
                'product_uom_qty':3,
                'product_uom':self.finished_product.uom_id.id,
                'price_unit':self.finished_product.list_price
            })],
            'pricelist_id':self.env.ref('product.list0').id,
            'company_id':self.company.id,
        }
        self.so=self.env['sale.order'].create(so_vals)
        #ValidatetheSO
        self.so.action_confirm()
        #Deliverthethreefinishedproducts
        pick=self.so.picking_ids
        #Tochecktheproductsonthepicking
        self.assertEqual(pick.move_lines.mapped('product_id'),self.component1|self.component2)
        wiz_act=pick.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()
        #Createtheinvoice
        self.so._create_invoices()
        self.invoice=self.so.invoice_ids
        #Changedtheinvoicedquantityofthefinishedproductto2
        move_form=Form(self.invoice)
        withmove_form.invoice_line_ids.edit(0)asline_form:
            line_form.quantity=2.0
        self.invoice=move_form.save()
        self.invoice.action_post()
        aml=self.invoice.line_ids
        aml_expense=aml.filtered(lambdal:l.is_anglo_saxon_lineandl.debit>0)
        aml_output=aml.filtered(lambdal:l.is_anglo_saxon_lineandl.credit>0)
        #CheckthatthecostofGoodSoldentriesareequalto2*(2*20+1*10)=100
        self.assertEqual(aml_expense.debit,100,"CostofGoodSoldentrymissingormismatching")
        self.assertEqual(aml_output.credit,100,"CostofGoodSoldentrymissingormismatching")

    deftest_03_sale_mrp_simple_kit_qty_delivered(self):
        """Testthatthequantitiesdeliveredarecorrectwhen
        asimplekitisorderedwithmultiplebackorders
        """

        #kit_1structure:
        #================

        #kit_1---|-component_a x2
        #         |-component_b x1
        #         |-component_c x3

        #Updatingthequantitiesinstocktoprevent
        #a'Notenoughinventory'warningmessage.
        stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.env['stock.quant']._update_available_quantity(self.component_a,stock_location,20)
        self.env['stock.quant']._update_available_quantity(self.component_b,stock_location,10)
        self.env['stock.quant']._update_available_quantity(self.component_c,stock_location,30)

        #Creationofasaleorderforx10kit_1
        partner=self.env['res.partner'].create({'name':'MyTestPartner'})
        f=Form(self.env['sale.order'])
        f.partner_id=partner
        withf.order_line.new()asline:
            line.product_id=self.kit_1
            line.product_uom_qty=10.0

        #ConfirmingtheSOtotriggerthepickingcreation
        so=f.save()
        so.action_confirm()

        #Checkpickingcreation
        self.assertEqual(len(so.picking_ids),1)
        picking_original=so.picking_ids[0]
        move_lines=picking_original.move_lines

        #Checkifthecorrectamountofstock.movesarecreated
        self.assertEqual(len(move_lines),3)

        #CheckifBoMiscreatedandisfora'Kit'
        bom_from_k1=self.env['mrp.bom']._bom_find(product=self.kit_1)
        self.assertEqual(self.bom_kit_1.id,bom_from_k1.id)
        self.assertEqual(bom_from_k1.type,'phantom')

        #Checkthere'sonly1orderlineontheSOandit'sforx10'kit_1'
        order_lines=so.order_line
        self.assertEqual(len(order_lines),1)
        order_line=order_lines[0]
        self.assertEqual(order_line.product_id.id,self.kit_1.id)
        self.assertEqual(order_line.product_uom_qty,10.0)

        #Checkifcorrectqtyisorderedforeachcomponentofthekit
        expected_quantities={
            self.component_a:20,
            self.component_b:10,
            self.component_c:30,
        }
        self._assert_quantities(move_lines,expected_quantities)

        #Processonlyx1ofthefirstcomponentthencreateabackorderforthemissingcomponents
        picking_original.move_lines.sorted()[0].write({'quantity_done':1})

        wiz_act=so.picking_ids[0].button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        #Checkthatthebackorderwascreated,nokitshouldbedeliveredatthispoint
        self.assertEqual(len(so.picking_ids),2)
        backorder_1=so.picking_ids-picking_original
        self.assertEqual(backorder_1.backorder_id.id,picking_original.id)
        self.assertEqual(order_line.qty_delivered,0)

        #Processonlyx6eachcomponenentinthepicking
        #Thencreateabackorderforthemissingcomponents
        backorder_1.move_lines.write({'quantity_done':6})
        wiz_act=backorder_1.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        #Checkthatabackorderiscreated
        self.assertEqual(len(so.picking_ids),3)
        backorder_2=so.picking_ids-picking_original-backorder_1
        self.assertEqual(backorder_2.backorder_id.id,backorder_1.id)

        #Withx6unitofeachcomponents,wecanonlymake2kits.
        #Soonly2kitsshouldbedelivered
        self.assertEqual(order_line.qty_delivered,2)

        #Processx3moreunitofeachcomponents:
        #-Nowonly3kitsshouldbedelivered
        #-Abackorderwillbecreated,theSOshouldhave3picking_idslinkedtoit.
        backorder_2.move_lines.write({'quantity_done':3})

        wiz_act=backorder_2.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        self.assertEqual(len(so.picking_ids),4)
        backorder_3=so.picking_ids-picking_original-backorder_2-backorder_1
        self.assertEqual(backorder_3.backorder_id.id,backorder_2.id)
        self.assertEqual(order_line.qty_delivered,3)

        #Addingmissingcomponents
        qty_to_process={
            self.component_a:10,
            self.component_b:1,
            self.component_c:21,
        }
        self._process_quantities(backorder_3.move_lines,qty_to_process)

        #Validatingthelastbackordernowit'scomplete
        backorder_3.button_validate()
        order_line._compute_qty_delivered()

        #Allkitsshouldbedelivered
        self.assertEqual(order_line.qty_delivered,10)

    deftest_04_sale_mrp_kit_qty_delivered(self):
        """Testthatthequantitiesdeliveredarecorrectwhen
        akitwithsubkitsisorderedwithmultiplebackordersandreturns
        """

        #'kit_parent'structure:
        #---------------------------
        #
        #kit_parent--|-kit_2x2--|-component_dx1
        #             |            |-kit_1x2-------|-component_a  x2
        #             |                               |-component_b  x1
        #             |                               |-component_c  x3
        #             |
        #             |-kit_3x1--|-component_fx1
        #             |            |-component_gx2
        #             |
        #             |-component_ex1

        #Updatingthequantitiesinstocktoprevent
        #a'Notenoughinventory'warningmessage.
        stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.env['stock.quant']._update_available_quantity(self.component_a,stock_location,56)
        self.env['stock.quant']._update_available_quantity(self.component_b,stock_location,28)
        self.env['stock.quant']._update_available_quantity(self.component_c,stock_location,84)
        self.env['stock.quant']._update_available_quantity(self.component_d,stock_location,14)
        self.env['stock.quant']._update_available_quantity(self.component_e,stock_location,7)
        self.env['stock.quant']._update_available_quantity(self.component_f,stock_location,14)
        self.env['stock.quant']._update_available_quantity(self.component_g,stock_location,28)

        #Creationofasaleorderforx7kit_parent
        partner=self.env['res.partner'].create({'name':'MyTestPartner'})
        f=Form(self.env['sale.order'])
        f.partner_id=partner
        withf.order_line.new()asline:
            line.product_id=self.kit_parent
            line.product_uom_qty=7.0

        so=f.save()
        so.action_confirm()

        #Checkpickingcreation,itsmovelinesshouldconcern
        #onlycomponents.Alsochecksthatthequantitiesarecorresponding
        #totheSO
        self.assertEqual(len(so.picking_ids),1)
        order_line=so.order_line[0]
        picking_original=so.picking_ids[0]
        move_lines=picking_original.move_lines
        products=move_lines.mapped('product_id')
        kits=[self.kit_parent,self.kit_3,self.kit_2,self.kit_1]
        components=[self.component_a,self.component_b,self.component_c,self.component_d,self.component_e,self.component_f,self.component_g]
        expected_quantities={
            self.component_a:56.0,
            self.component_b:28.0,
            self.component_c:84.0,
            self.component_d:14.0,
            self.component_e:7.0,
            self.component_f:14.0,
            self.component_g:28.0
        }

        self.assertEqual(len(move_lines),7)
        self.assertTrue(notany(kitinproductsforkitinkits))
        self.assertTrue(all(componentinproductsforcomponentincomponents))
        self._assert_quantities(move_lines,expected_quantities)

        #Processonly7unitsofeachcomponent
        qty_to_process=7
        move_lines.write({'quantity_done':qty_to_process})

        #Createabackorderforthemissingcomponenents
        wiz_act=picking_original.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        #Checkthatabackordediscreated
        self.assertEqual(len(so.picking_ids),2)
        backorder_1=so.picking_ids-picking_original
        self.assertEqual(backorder_1.backorder_id.id,picking_original.id)

        #Evenifsomecomponentsaredeliveredcompletely,
        #noKitParentshouldbedelivered
        self.assertEqual(order_line.qty_delivered,0)

        #Processjustenoughcomponentstomake1kit_parent
        qty_to_process={
            self.component_a:1,
            self.component_c:5,
        }
        self._process_quantities(backorder_1.move_lines,qty_to_process)

        #Createabackorderforthemissingcomponenents
        wiz_act=backorder_1.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        #Only1kit_parentshouldbedeliveredatthispoint
        self.assertEqual(order_line.qty_delivered,1)

        #Checkthatthesecondbackorderiscreated
        self.assertEqual(len(so.picking_ids),3)
        backorder_2=so.picking_ids-picking_original-backorder_1
        self.assertEqual(backorder_2.backorder_id.id,backorder_1.id)

        #Setthecomponentsquantitiesthatbackorder_2shouldhave
        expected_quantities={
            self.component_a:48,
            self.component_b:21,
            self.component_c:72,
            self.component_d:7,
            self.component_f:7,
            self.component_g:21
        }

        #Checkthatthecomputedquantitiesarematchingthetheoricalones.
        #Sincecomponent_ewastotallyprocessed,thiscomponenentshouldn'tbe
        #presentinbackorder_2
        self.assertEqual(len(backorder_2.move_lines),6)
        move_comp_e=backorder_2.move_lines.filtered(lambdam:m.product_id.id==self.component_e.id)
        self.assertFalse(move_comp_e)
        self._assert_quantities(backorder_2.move_lines,expected_quantities)

        #Processenoughcomponentstomakex3kit_parents
        qty_to_process={
            self.component_a:16,
            self.component_b:5,
            self.component_c:24,
            self.component_g:5
        }
        self._process_quantities(backorder_2.move_lines,qty_to_process)

        #Createabackorderforthemissingcomponenents
        wiz_act=backorder_2.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        #Checkthatx3kit_parentsareindeeddelivered
        self.assertEqual(order_line.qty_delivered,3)

        #Checkthatthethirdbackorderiscreated
        self.assertEqual(len(so.picking_ids),4)
        backorder_3=so.picking_ids-(picking_original+backorder_1+backorder_2)
        self.assertEqual(backorder_3.backorder_id.id,backorder_2.id)

        #Checkthecomponentsquantitiesthatbackorder_3shouldhave
        expected_quantities={
            self.component_a:32,
            self.component_b:16,
            self.component_c:48,
            self.component_d:7,
            self.component_f:7,
            self.component_g:16
        }
        self._assert_quantities(backorder_3.move_lines,expected_quantities)

        #Processallmissingcomponents
        self._process_quantities(backorder_3.move_lines,expected_quantities)

        #Validatingthelastbackordernowit'scomplete.
        #Allkitsshouldbedelivered
        backorder_3.button_validate()
        self.assertEqual(order_line.qty_delivered,7.0)

        #Returnallcomponentsprocessedbybackorder_3
        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=backorder_3.ids,active_id=backorder_3.ids[0],
            active_model='stock.picking'))
        return_wiz=stock_return_picking_form.save()
        forreturn_moveinreturn_wiz.product_return_moves:
            return_move.write({
                'quantity':expected_quantities[return_move.product_id],
                'to_refund':True
            })
        res=return_wiz.create_returns()
        return_pick=self.env['stock.picking'].browse(res['res_id'])

        #Processallcomponentsandvalidatethepicking
        wiz_act=return_pick.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        #Nowquantitydeliveredshouldbe3again
        self.assertEqual(order_line.qty_delivered,3)

        stock_return_picking_form=Form(self.env['stock.return.picking']
            .with_context(active_ids=return_pick.ids,active_id=return_pick.ids[0],
            active_model='stock.picking'))
        return_wiz=stock_return_picking_form.save()
        formoveinreturn_wiz.product_return_moves:
            move.quantity=expected_quantities[move.product_id]
        res=return_wiz.create_returns()
        return_of_return_pick=self.env['stock.picking'].browse(res['res_id'])

        #Processallcomponentsexceptoneofeach
        formoveinreturn_of_return_pick.move_lines:
            move.write({
                'quantity_done':expected_quantities[move.product_id]-1,
                'to_refund':True
            })

        wiz_act=return_of_return_pick.button_validate()
        Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()

        #Asoneofeachcomponentismissing,only6kit_parentsshouldbedelivered
        self.assertEqual(order_line.qty_delivered,6)

        #Checkthatthe4thbackorderiscreated.
        self.assertEqual(len(so.picking_ids),7)
        backorder_4=so.picking_ids-(picking_original+backorder_1+backorder_2+backorder_3+return_of_return_pick+return_pick)
        self.assertEqual(backorder_4.backorder_id.id,return_of_return_pick.id)

        #Checkthecomponentsquantitiesthatbackorder_4shouldhave
        formoveinbackorder_4.move_lines:
            self.assertEqual(move.product_qty,1)

    @mute_logger('flectra.tests.common.onchange')
    deftest_05_mrp_sale_kit_availability(self):
        """
        Checkthatthe'Notenoughinventory'warningmessageshowscorrect
        informationswhenakitisordered
        """

        warehouse_1=self.env['stock.warehouse'].create({
            'name':'Warehouse1',
            'code':'WH1'
        })
        warehouse_2=self.env['stock.warehouse'].create({
            'name':'Warehouse2',
            'code':'WH2'
        })

        #Thoseareallcomponenentsneededtomakekit_parents
        components=[self.component_a,self.component_b,self.component_c,self.component_d,self.component_e,
                      self.component_f,self.component_g]

        #Setenoughquantitiestomake1kit_uom_in_kitinWH1
        self.env['stock.quant']._update_available_quantity(self.component_a,warehouse_1.lot_stock_id,8)
        self.env['stock.quant']._update_available_quantity(self.component_b,warehouse_1.lot_stock_id,4)
        self.env['stock.quant']._update_available_quantity(self.component_c,warehouse_1.lot_stock_id,12)
        self.env['stock.quant']._update_available_quantity(self.component_d,warehouse_1.lot_stock_id,2)
        self.env['stock.quant']._update_available_quantity(self.component_e,warehouse_1.lot_stock_id,1)
        self.env['stock.quant']._update_available_quantity(self.component_f,warehouse_1.lot_stock_id,2)
        self.env['stock.quant']._update_available_quantity(self.component_g,warehouse_1.lot_stock_id,4)

        #SetquantitiesonWH2,butnotenoughtomake1kit_parent
        self.env['stock.quant']._update_available_quantity(self.component_a,warehouse_2.lot_stock_id,7)
        self.env['stock.quant']._update_available_quantity(self.component_b,warehouse_2.lot_stock_id,3)
        self.env['stock.quant']._update_available_quantity(self.component_c,warehouse_2.lot_stock_id,12)
        self.env['stock.quant']._update_available_quantity(self.component_d,warehouse_2.lot_stock_id,1)
        self.env['stock.quant']._update_available_quantity(self.component_e,warehouse_2.lot_stock_id,1)
        self.env['stock.quant']._update_available_quantity(self.component_f,warehouse_2.lot_stock_id,1)
        self.env['stock.quant']._update_available_quantity(self.component_g,warehouse_2.lot_stock_id,4)

        #Creationofasaleorderforx7kit_parent
        qty_ordered=7
        f=Form(self.env['sale.order'])
        f.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        f.warehouse_id=warehouse_2
        withf.order_line.new()asline:
            line.product_id=self.kit_parent
            line.product_uom_qty=qty_ordered
        so=f.save()
        order_line=so.order_line[0]

        #CheckthatnotenoughenoughquantitiesareavailableinthewarehousesetintheSO
        #butthereareenoughquantitiesinWarehouse1for1kit_parent
        kit_parent_wh_order=self.kit_parent.with_context(warehouse=so.warehouse_id.id)

        #CheckthatnotenoughenoughquantitiesareavailableinthewarehousesetintheSO
        #butthereareenoughquantitiesinWarehouse1for1kit_parent
        self.assertEqual(kit_parent_wh_order.virtual_available,0)
        kit_parent_wh_order.invalidate_cache()
        kit_parent_wh1=self.kit_parent.with_context(warehouse=warehouse_1.id)
        self.assertEqual(kit_parent_wh1.virtual_available,1)

        #Checktherearn'tenoughquantitiesavailableforthesaleorder
        self.assertTrue(float_compare(order_line.virtual_available_at_date-order_line.product_uom_qty,0,precision_rounding=line.product_uom.rounding)==-1)

        #WereceiveenougofeachcomponentinWarehouse2tomake3kit_parent
        qty_to_process={
            self.component_a:(17,self.uom_unit),
            self.component_b:(12,self.uom_unit),
            self.component_c:(25,self.uom_unit),
            self.component_d:(5,self.uom_unit),
            self.component_e:(2,self.uom_unit),
            self.component_f:(5,self.uom_unit),
            self.component_g:(8,self.uom_unit),
        }
        self._create_move_quantities(qty_to_process,components,warehouse_2)

        #As'Warehouse2'isthewarehouselinkedtotheSO,3kitsshouldbeavailable
        #ButthequantityavailableinWarehouse1shouldstay1
        kit_parent_wh_order=self.kit_parent.with_context(warehouse=so.warehouse_id.id)
        self.assertEqual(kit_parent_wh_order.virtual_available,3)
        kit_parent_wh_order.invalidate_cache()
        kit_parent_wh1=self.kit_parent.with_context(warehouse=warehouse_1.id)
        self.assertEqual(kit_parent_wh1.virtual_available,1)

        #Checktherearn'tenoughquantitiesavailableforthesaleorder
        self.assertTrue(float_compare(order_line.virtual_available_at_date-order_line.product_uom_qty,0,precision_rounding=line.product_uom.rounding)==-1)

        #WereceiveenoughofeachcomponentinWarehouse2tomake7kit_parent
        qty_to_process={
            self.component_a:(32,self.uom_unit),
            self.component_b:(16,self.uom_unit),
            self.component_c:(48,self.uom_unit),
            self.component_d:(8,self.uom_unit),
            self.component_e:(4,self.uom_unit),
            self.component_f:(8,self.uom_unit),
            self.component_g:(16,self.uom_unit),
        }
        self._create_move_quantities(qty_to_process,components,warehouse_2)

        #Enoughquantitiesshouldbeavailable,nowarningmessageshouldbedisplayed
        kit_parent_wh_order=self.kit_parent.with_context(warehouse=so.warehouse_id.id)
        self.assertEqual(kit_parent_wh_order.virtual_available,7)

    deftest_06_kit_qty_delivered_mixed_uom(self):
        """
        Checkthatthequantitiesdeliveredarecorrectwhenakitinvolves
        multipleUoMsonitscomponents
        """
        #Createsomecomponents
        component_uom_unit=self._create_product('CompUnit',self.uom_unit)
        component_uom_dozen=self._create_product('CompDozen',self.uom_dozen)
        component_uom_kg=self._create_product('CompKg',self.uom_kg)

        #Createakit'kit_uom_1':
        #-----------------------
        #
        #kit_uom_1--|-component_uom_unit   x2Test-Dozen
        #            |-component_uom_dozen  x1Test-Dozen
        #            |-component_uom_kg     x3Test-G

        kit_uom_1=self._create_product('Kit1',self.uom_unit)

        bom_kit_uom_1=self.env['mrp.bom'].create({
            'product_tmpl_id':kit_uom_1.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine=self.env['mrp.bom.line']
        BomLine.create({
            'product_id':component_uom_unit.id,
            'product_qty':2.0,
            'product_uom_id':self.uom_dozen.id,
            'bom_id':bom_kit_uom_1.id})
        BomLine.create({
            'product_id':component_uom_dozen.id,
            'product_qty':1.0,
            'product_uom_id':self.uom_dozen.id,
            'bom_id':bom_kit_uom_1.id})
        BomLine.create({
            'product_id':component_uom_kg.id,
            'product_qty':3.0,
            'product_uom_id':self.uom_gm.id,
            'bom_id':bom_kit_uom_1.id})

        #Updatingthequantitiesinstocktoprevent
        #a'Notenoughinventory'warningmessage.
        stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.env['stock.quant']._update_available_quantity(component_uom_unit,stock_location,240)
        self.env['stock.quant']._update_available_quantity(component_uom_dozen,stock_location,10)
        self.env['stock.quant']._update_available_quantity(component_uom_kg,stock_location,0.03)

        #Creationofasaleorderforx10kit_1
        partner=self.env['res.partner'].create({'name':'MyTestPartner'})
        f=Form(self.env['sale.order'])
        f.partner_id=partner
        withf.order_line.new()asline:
            line.product_id=kit_uom_1
            line.product_uom_qty=10.0

        so=f.save()
        so.action_confirm()

        picking_original=so.picking_ids[0]
        move_lines=picking_original.move_lines
        order_line=so.order_line[0]

        #Checkthatthequantitiesonthepickingaretheoneexpectedforeachcomponents
        formlinmove_lines:
            corr_bom_line=bom_kit_uom_1.bom_line_ids.filtered(lambdab:b.product_id.id==ml.product_id.id)
            computed_qty=ml.product_uom._compute_quantity(ml.product_uom_qty,corr_bom_line.product_uom_id)
            self.assertEqual(computed_qty,order_line.product_uom_qty*corr_bom_line.product_qty)

        #Processeenoughcomponenentsinthepickingtomake2kit_uom_1
        #Thencreateabackorderforthemissingcomponents
        qty_to_process={
            component_uom_unit:48,
            component_uom_dozen:3,
            component_uom_kg:0.006
        }
        self._process_quantities(move_lines,qty_to_process)
        res=move_lines.picking_id.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()

        #Checkthatabackorderiscreated
        self.assertEqual(len(so.picking_ids),2)
        backorder_1=so.picking_ids-picking_original
        self.assertEqual(backorder_1.backorder_id.id,picking_original.id)

        #Only2kitsshouldbedelivered
        self.assertEqual(order_line.qty_delivered,2)

        #Addingmissingcomponents
        qty_to_process={
            component_uom_unit:192,
            component_uom_dozen:7,
            component_uom_kg:0.024
        }
        self._process_quantities(backorder_1.move_lines,qty_to_process)

        #Validatingthelastbackordernowit'scomplete
        backorder_1.button_validate()
        order_line._compute_qty_delivered()
        #Allkitsshouldbedelivered
        self.assertEqual(order_line.qty_delivered,10)

    @mute_logger('flectra.tests.common.onchange')
    deftest_07_kit_availability_mixed_uom(self):
        """
        Checkthatthe'Notenoughinventory'warningmessagedisplayscorrect
        informationswhenakitwithmultipleUoMsonitscomponentsisordered
        """

        #Createsomecomponents
        component_uom_unit=self._create_product('CompUnit',self.uom_unit)
        component_uom_dozen=self._create_product('CompDozen',self.uom_dozen)
        component_uom_kg=self._create_product('CompKg',self.uom_kg)
        component_uom_gm=self._create_product('Compg',self.uom_gm)
        components=[component_uom_unit,component_uom_dozen,component_uom_kg,component_uom_gm]

        #Createakit'kit_uom_in_kit':
        #-----------------------
        #kit_uom_in_kit--|-component_uom_gm x3Test-KG
        #                 |-kit_uom_1        x2Test-Dozen--|-component_uom_unit   x2Test-Dozen
        #                                                      |-component_uom_dozen  x1Test-Dozen
        #                                                      |-component_uom_kg     x5Test-G

        kit_uom_1=self._create_product('SubKit1',self.uom_unit)
        kit_uom_in_kit=self._create_product('ParentKit',self.uom_unit)

        bom_kit_uom_1=self.env['mrp.bom'].create({
            'product_tmpl_id':kit_uom_1.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine=self.env['mrp.bom.line']
        BomLine.create({
            'product_id':component_uom_unit.id,
            'product_qty':2.0,
            'product_uom_id':self.uom_dozen.id,
            'bom_id':bom_kit_uom_1.id})
        BomLine.create({
            'product_id':component_uom_dozen.id,
            'product_qty':1.0,
            'product_uom_id':self.uom_dozen.id,
            'bom_id':bom_kit_uom_1.id})
        BomLine.create({
            'product_id':component_uom_kg.id,
            'product_qty':5.0,
            'product_uom_id':self.uom_gm.id,
            'bom_id':bom_kit_uom_1.id})

        bom_kit_uom_in_kit=self.env['mrp.bom'].create({
            'product_tmpl_id':kit_uom_in_kit.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom'})

        BomLine.create({
            'product_id':component_uom_gm.id,
            'product_qty':3.0,
            'product_uom_id':self.uom_kg.id,
            'bom_id':bom_kit_uom_in_kit.id})
        BomLine.create({
            'product_id':kit_uom_1.id,
            'product_qty':2.0,
            'product_uom_id':self.uom_dozen.id,
            'bom_id':bom_kit_uom_in_kit.id})

        #Createasimplewarehousetoreceivessomeproducts
        warehouse_1=self.env['stock.warehouse'].create({
            'name':'Warehouse1',
            'code':'WH1'
        })

        #Setenoughquantitiestomake1kit_uom_in_kitinWH1
        self.env['stock.quant']._update_available_quantity(component_uom_unit,warehouse_1.lot_stock_id,576)
        self.env['stock.quant']._update_available_quantity(component_uom_dozen,warehouse_1.lot_stock_id,24)
        self.env['stock.quant']._update_available_quantity(component_uom_kg,warehouse_1.lot_stock_id,0.12)
        self.env['stock.quant']._update_available_quantity(component_uom_gm,warehouse_1.lot_stock_id,3000)

        #Creationofasaleorderforx5kit_uom_in_kit
        qty_ordered=5
        f=Form(self.env['sale.order'])
        f.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        f.warehouse_id=warehouse_1
        withf.order_line.new()asline:
            line.product_id=kit_uom_in_kit
            line.product_uom_qty=qty_ordered

        so=f.save()
        order_line=so.order_line[0]

        #CheckthatnotenoughenoughquantitiesareavailableinthewarehousesetintheSO
        #butthereareenoughquantitiesinWarehouse1for1kit_parent
        kit_uom_in_kit.with_context(warehouse=warehouse_1.id)._compute_quantities()
        virtual_available_wh_order=kit_uom_in_kit.virtual_available
        self.assertEqual(virtual_available_wh_order,1)

        #Checktherearn'tenoughquantitiesavailableforthesaleorder
        self.assertTrue(float_compare(order_line.virtual_available_at_date-order_line.product_uom_qty,0,precision_rounding=line.product_uom.rounding)==-1)

        #WereceiveenoughofeachcomponentinWarehouse1tomake3kit_uom_in_kit.
        #Movesarecreatedinsteadofonlyupdatingthequantquantitiesinordertotriggereverycomputefields.
        qty_to_process={
            component_uom_unit:(1152,self.uom_unit),
            component_uom_dozen:(48,self.uom_dozen),
            component_uom_kg:(0.24,self.uom_kg),
            component_uom_gm:(6000,self.uom_gm)
        }
        self._create_move_quantities(qty_to_process,components,warehouse_1)

        #Checktherearn'tenoughquantitiesavailableforthesaleorder
        self.assertTrue(float_compare(order_line.virtual_available_at_date-order_line.product_uom_qty,0,precision_rounding=line.product_uom.rounding)==-1)
        kit_uom_in_kit.with_context(warehouse=warehouse_1.id)._compute_quantities()
        virtual_available_wh_order=kit_uom_in_kit.virtual_available
        self.assertEqual(virtual_available_wh_order,3)

        #Weprocessenoughquantitiestohaveenoughkit_uom_in_kitavailableforthesaleorder.
        self._create_move_quantities(qty_to_process,components,warehouse_1)

        #Wecheckthatenoughquantitieswereprocessedtosell5kit_uom_in_kit
        kit_uom_in_kit.with_context(warehouse=warehouse_1.id)._compute_quantities()
        self.assertEqual(kit_uom_in_kit.virtual_available,5)

    deftest_10_sale_mrp_kits_routes(self):

        #Createakit'kit_1':
        #-----------------------
        #
        #kit_1--|-component_shelf1  x3
        #        |-component_shelf2  x2

        stock_location_components=self.env['stock.location'].create({
            'name':'Shelf1',
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
        })
        stock_location_14=self.env['stock.location'].create({
            'name':'Shelf2',
            'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
        })

        kit_1=self._create_product('Kit1',self.uom_unit)
        component_shelf1=self._create_product('CompShelf1',self.uom_unit)
        component_shelf2=self._create_product('CompShelf2',self.uom_unit)

        withForm(self.env['mrp.bom'])asbom:
            bom.product_tmpl_id=kit_1.product_tmpl_id
            bom.product_qty=1
            bom.product_uom_id=self.uom_unit
            bom.type='phantom'
            withbom.bom_line_ids.new()asline:
                line.product_id=component_shelf1
                line.product_qty=3
                line.product_uom_id=self.uom_unit
            withbom.bom_line_ids.new()asline:
                line.product_id=component_shelf2
                line.product_qty=2
                line.product_uom_id=self.uom_unit

        #Creating2specificroutesforeachofthecomponentsofthekit
        route_shelf1=self.env['stock.location.route'].create({
            'name':'Shelf1->Customer',
            'product_selectable':True,
            'rule_ids':[(0,0,{
                'name':'Shelf1->Customer',
                'action':'pull',
                'picking_type_id':self.company_data['default_warehouse'].in_type_id.id,
                'location_src_id':stock_location_components.id,
                'location_id':self.ref('stock.stock_location_customers'),
            })],
        })

        route_shelf2=self.env['stock.location.route'].create({
            'name':'Shelf2->Customer',
            'product_selectable':True,
            'rule_ids':[(0,0,{
                'name':'Shelf2->Customer',
                'action':'pull',
                'picking_type_id':self.company_data['default_warehouse'].in_type_id.id,
                'location_src_id':stock_location_14.id,
                'location_id':self.ref('stock.stock_location_customers'),
            })],
        })

        component_shelf1.write({
            'route_ids':[(4,route_shelf1.id)]})
        component_shelf2.write({
            'route_ids':[(4,route_shelf2.id)]})

        #Setenoughquantitiestomake1kit_uom_in_kitinWH1
        self.env['stock.quant']._update_available_quantity(component_shelf1,self.company_data['default_warehouse'].lot_stock_id,15)
        self.env['stock.quant']._update_available_quantity(component_shelf2,self.company_data['default_warehouse'].lot_stock_id,10)

        #Creatingasaleorderfor5kitsandconfirmingit
        order_form=Form(self.env['sale.order'])
        order_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        withorder_form.order_line.new()asline:
            line.product_id=kit_1
            line.product_uom=self.uom_unit
            line.product_uom_qty=5
        order=order_form.save()
        order.action_confirm()

        #Nowwecheckthattheroutesofthecomponentswereapplied,inordertomakesuretheroutesset
        #onthekititselfareignored
        self.assertEqual(len(order.picking_ids),2)
        self.assertEqual(len(order.picking_ids[0].move_lines),1)
        self.assertEqual(len(order.picking_ids[1].move_lines),1)
        moves=order.picking_ids.mapped('move_lines')
        move_shelf1=moves.filtered(lambdam:m.product_id==component_shelf1)
        move_shelf2=moves.filtered(lambdam:m.product_id==component_shelf2)
        self.assertEqual(move_shelf1.location_id.id,stock_location_components.id)
        self.assertEqual(move_shelf1.location_dest_id.id,self.ref('stock.stock_location_customers'))
        self.assertEqual(move_shelf2.location_id.id,stock_location_14.id)
        self.assertEqual(move_shelf2.location_dest_id.id,self.ref('stock.stock_location_customers'))

    deftest_11_sale_mrp_explode_kits_uom_quantities(self):

        #Createakit'kit_1':
        #-----------------------
        #
        #2xDozenskit_1--|-component_unit  x6Units
        #                  |-component_kg    x7Kg

        kit_1=self._create_product('Kit1',self.uom_unit)
        component_unit=self._create_product('CompUnit',self.uom_unit)
        component_kg=self._create_product('CompKg',self.uom_kg)

        withForm(self.env['mrp.bom'])asbom:
            bom.product_tmpl_id=kit_1.product_tmpl_id
            bom.product_qty=2
            bom.product_uom_id=self.uom_dozen
            bom.type='phantom'
            withbom.bom_line_ids.new()asline:
                line.product_id=component_unit
                line.product_qty=6
                line.product_uom_id=self.uom_unit
            withbom.bom_line_ids.new()asline:
                line.product_id=component_kg
                line.product_qty=7
                line.product_uom_id=self.uom_kg

        #Createasimplewarehousetoreceivessomeproducts
        warehouse_1=self.env['stock.warehouse'].create({
            'name':'Warehouse1',
            'code':'WH1'
        })
        #Setenoughquantitiestomake1Test-Dozenkit_uom_in_kit
        self.env['stock.quant']._update_available_quantity(component_unit,warehouse_1.lot_stock_id,12)
        self.env['stock.quant']._update_available_quantity(component_kg,warehouse_1.lot_stock_id,14)

        #Creatingasaleorderfor3Unitsofkit_1andconfirmingit
        order_form=Form(self.env['sale.order'])
        order_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        order_form.warehouse_id=warehouse_1
        withorder_form.order_line.new()asline:
            line.product_id=kit_1
            line.product_uom=self.uom_unit
            line.product_uom_qty=2
        order=order_form.save()
        order.action_confirm()

        #Nowwecheckthattheroutesofthecomponentswereapplied,inordertomakesuretheroutesset
        #onthekititselfareignored
        self.assertEqual(len(order.picking_ids),1)
        self.assertEqual(len(order.picking_ids[0].move_lines),2)

        #Finally,wecheckthequantitiesforeachcomponentonthepicking
        move_component_unit=order.picking_ids[0].move_lines.filtered(lambdam:m.product_id==component_unit)
        move_component_kg=order.picking_ids[0].move_lines-move_component_unit
        self.assertEqual(move_component_unit.product_uom_qty,0.5)
        self.assertEqual(move_component_kg.product_uom_qty,0.58)

    deftest_product_type_service_1(self):
        route_manufacture=self.company_data['default_warehouse'].manufacture_pull_id.route_id.id
        route_mto=self.company_data['default_warehouse'].mto_pull_id.route_id.id
        self.uom_unit=self.env.ref('uom.product_uom_unit')

        #Createfinishedproduct
        finished_product=self.env['product.product'].create({
            'name':'Geyser',
            'type':'product',
            'route_ids':[(4,route_mto),(4,route_manufacture)],
        })

        #Createservicetypeproduct
        product_raw=self.env['product.product'].create({
            'name':'rawGeyser',
            'type':'service',
        })

        #Createbomforfinishproduct
        bom=self.env['mrp.bom'].create({
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[(5,0),(0,0,{'product_id':product_raw.id})]
        })

        #Createsaleorder
        sale_form=Form(self.env['sale.order'])
        sale_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        withsale_form.order_line.new()asline:
            line.name=finished_product.name
            line.product_id=finished_product
            line.product_uom_qty=1.0
            line.product_uom=self.uom_unit
            line.price_unit=10.0
        sale_order=sale_form.save()

        sale_order.action_confirm()

        mo=self.env['mrp.production'].search([('product_id','=',finished_product.id)])

        self.assertTrue(mo,'Manufacturingordercreated.')

    deftest_cancel_flow_1(self):
        """SellaMTO/manufactureproduct.

        Cancelthedeliveryandtheproductionorder.Thenduplicate
        thedelivery.Anotherproductionordershouldbecreated."""
        route_manufacture=self.company_data['default_warehouse'].manufacture_pull_id.route_id.id
        route_mto=self.company_data['default_warehouse'].mto_pull_id.route_id.id
        self.uom_unit=self.env.ref('uom.product_uom_unit')

        #Createfinishedproduct
        finished_product=self.env['product.product'].create({
            'name':'Geyser',
            'type':'product',
            'route_ids':[(4,route_mto),(4,route_manufacture)],
        })

        product_raw=self.env['product.product'].create({
            'name':'rawGeyser',
            'type':'product',
        })

        #Createbomforfinishproduct
        bom=self.env['mrp.bom'].create({
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[(5,0),(0,0,{'product_id':product_raw.id})]
        })

        #Createsaleorder
        sale_form=Form(self.env['sale.order'])
        sale_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        withsale_form.order_line.new()asline:
            line.name=finished_product.name
            line.product_id=finished_product
            line.product_uom_qty=1.0
            line.product_uom=self.uom_unit
            line.price_unit=10.0
        sale_order=sale_form.save()

        sale_order.action_confirm()

        mo=self.env['mrp.production'].search([('product_id','=',finished_product.id)])
        delivery=sale_order.picking_ids
        delivery.action_cancel()
        mo.action_cancel()
        copied_delivery=delivery.copy()
        copied_delivery.action_confirm()
        mos=self.env['mrp.production'].search([('product_id','=',finished_product.id)])
        self.assertEqual(len(mos),1)
        self.assertEqual(mos.state,'cancel')

    deftest_cancel_flow_2(self):
        """SellaMTO/manufactureproduct.

        Canceltheproductionorderandthedelivery.Thenduplicate
        thedelivery.Anotherproductionordershouldbecreated."""
        route_manufacture=self.company_data['default_warehouse'].manufacture_pull_id.route_id.id
        route_mto=self.company_data['default_warehouse'].mto_pull_id.route_id.id
        self.uom_unit=self.env.ref('uom.product_uom_unit')

        #Createfinishedproduct
        finished_product=self.env['product.product'].create({
            'name':'Geyser',
            'type':'product',
            'route_ids':[(4,route_mto),(4,route_manufacture)],
        })

        product_raw=self.env['product.product'].create({
            'name':'rawGeyser',
            'type':'product',
        })

        #Createbomforfinishproduct
        bom=self.env['mrp.bom'].create({
            'product_id':finished_product.id,
            'product_tmpl_id':finished_product.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[(5,0),(0,0,{'product_id':product_raw.id})]
        })

        #Createsaleorder
        sale_form=Form(self.env['sale.order'])
        sale_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        withsale_form.order_line.new()asline:
            line.name=finished_product.name
            line.product_id=finished_product
            line.product_uom_qty=1.0
            line.product_uom=self.uom_unit
            line.price_unit=10.0
        sale_order=sale_form.save()

        sale_order.action_confirm()

        mo=self.env['mrp.production'].search([('product_id','=',finished_product.id)])
        delivery=sale_order.picking_ids
        mo.action_cancel()
        delivery.action_cancel()
        copied_delivery=delivery.copy()
        copied_delivery.action_confirm()
        mos=self.env['mrp.production'].search([('product_id','=',finished_product.id)])
        self.assertEqual(len(mos),1)
        self.assertEqual(mos.state,'cancel')

    deftest_12_sale_mrp_anglo_saxon_variant(self):
        """Testthepriceunitofkitwithvariants"""
        #Checkthatthecorrectbomareselectedwhencomputingprice_unitforCOGS

        self.env.company.currency_id=self.env.ref('base.USD')
        self.uom_unit=self.UoM.create({
            'name':'Test-Unit',
            'category_id':self.categ_unit.id,
            'factor':1,
            'uom_type':'bigger',
            'rounding':1.0})
        self.company=self.company_data['company']
        self.company.anglo_saxon_accounting=True
        self.partner=self.env['res.partner'].create({'name':'MyTestPartner'})
        self.category=self.env.ref('product.product_category_1').copy({'name':'Testcategory','property_valuation':'real_time','property_cost_method':'fifo'})
        account_type=self.env['account.account.type'].create({'name':'RCVtype','type':'other','internal_group':'asset'})
        self.account_receiv=self.env['account.account'].create({'name':'Receivable','code':'RCV00','user_type_id':account_type.id,'reconcile':True})
        account_expense=self.env['account.account'].create({'name':'Expense','code':'EXP00','user_type_id':account_type.id,'reconcile':True})
        account_output=self.env['account.account'].create({'name':'Output','code':'OUT00','user_type_id':account_type.id,'reconcile':True})
        account_valuation=self.env['account.account'].create({'name':'Valuation','code':'STV00','user_type_id':account_type.id,'reconcile':True})
        self.partner.property_account_receivable_id=self.account_receiv
        self.category.property_account_income_categ_id=self.account_receiv
        self.category.property_account_expense_categ_id=account_expense
        self.category.property_stock_account_input_categ_id=self.account_receiv
        self.category.property_stock_account_output_categ_id=account_output
        self.category.property_stock_valuation_account_id=account_valuation
        self.category.property_stock_journal=self.env['account.journal'].create({'name':'Stockjournal','type':'sale','code':'STK00'})

        #Createvariantattributes
        self.prod_att_1=self.env['product.attribute'].create({'name':'Color'})
        self.prod_attr1_v1=self.env['product.attribute.value'].create({'name':'red','attribute_id':self.prod_att_1.id,'sequence':1})
        self.prod_attr1_v2=self.env['product.attribute.value'].create({'name':'blue','attribute_id':self.prod_att_1.id,'sequence':2})

        #CreateProducttemplatewithvariants
        self.product_template=self.env['product.template'].create({
            'name':'ProductTemplate',
            'type':'product',
            'uom_id':self.uom_unit.id,
            'invoice_policy':'delivery',
            'categ_id':self.category.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.prod_att_1.id,
                'value_ids':[(6,0,[self.prod_attr1_v1.id,self.prod_attr1_v2.id])]
            })]
        })

        #Getproductvariant
        self.pt_attr1_v1=self.product_template.attribute_line_ids[0].product_template_value_ids[0]
        self.pt_attr1_v2=self.product_template.attribute_line_ids[0].product_template_value_ids[1]
        self.variant_1=self.product_template._get_variant_for_combination(self.pt_attr1_v1)
        self.variant_2=self.product_template._get_variant_for_combination(self.pt_attr1_v2)

        defcreate_simple_bom_for_product(product,name,price):
            component=self.env['product.product'].create({
                'name':'Component'+name,
                'type':'product',
                'uom_id':self.uom_unit.id,
                'categ_id':self.category.id,
                'standard_price':price
            })
            self.env['stock.quant'].sudo().create({
                'product_id':component.id,
                'location_id':self.company_data['default_warehouse'].lot_stock_id.id,
                'quantity':10.0,
            })
            bom=self.env['mrp.bom'].create({
                'product_tmpl_id':self.product_template.id,
                'product_id':product.id,
                'product_qty':1.0,
                'type':'phantom'
            })
            self.env['mrp.bom.line'].create({
                'product_id':component.id,
                'product_qty':1.0,
                'bom_id':bom.id
            })

        create_simple_bom_for_product(self.variant_1,"V1",20)
        create_simple_bom_for_product(self.variant_2,"V2",10)

        defcreate_post_sale_order(product):
            so_vals={
                'partner_id':self.partner.id,
                'partner_invoice_id':self.partner.id,
                'partner_shipping_id':self.partner.id,
                'order_line':[(0,0,{
                    'name':product.name,
                    'product_id':product.id,
                    'product_uom_qty':2,
                    'product_uom':product.uom_id.id,
                    'price_unit':product.list_price
                })],
                'pricelist_id':self.env.ref('product.list0').id,
                'company_id':self.company.id,
            }
            so=self.env['sale.order'].create(so_vals)
            #ValidatetheSO
            so.action_confirm()
            #Deliverthethreefinishedproducts
            pick=so.picking_ids
            #Tochecktheproductsonthepicking
            wiz_act=pick.button_validate()
            wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
            wiz.process()
            #Createtheinvoice
            so._create_invoices()
            invoice=so.invoice_ids
            invoice.action_post()
            returninvoice

        #CreateaSOforvariant1
        self.invoice_1=create_post_sale_order(self.variant_1)
        self.invoice_2=create_post_sale_order(self.variant_2)

        defcheck_cogs_entry_values(invoice,expected_value):
            aml=invoice.line_ids
            aml_expense=aml.filtered(lambdal:l.is_anglo_saxon_lineandl.debit>0)
            aml_output=aml.filtered(lambdal:l.is_anglo_saxon_lineandl.credit>0)
            self.assertEqual(aml_expense.debit,expected_value,"CostofGoodSoldentrymissingormismatchingforvariant")
            self.assertEqual(aml_output.credit,expected_value,"CostofGoodSoldentrymissingormismatchingforvariant")

        #CheckthatthecostofGoodSoldentriesforvariant1areequalto2*20=40
        check_cogs_entry_values(self.invoice_1,40)
        #CheckthatthecostofGoodSoldentriesforvariant2areequalto2*10=20
        check_cogs_entry_values(self.invoice_2,20)

    deftest_13_so_return_kit(self):
        """
        TestthatwhenreturningaSOcontainingonlyakitthatcontainsanotherkit,the
        SOdeliveredquantitiesissetto0(withtheall-or-nothingpolicy).
        Products:
            MainKit
            NestedKit
            Screw
        BoMs:
            MainKitBoM(kit),recipe:
                NestedKitBom(kit),recipe:
                    Screw
        Businessflow:
            Createthose
            CreateaSalesordersellingoneMainKitBoM
            Confirmthesalesorder
            Validatethedelivery(outgoing)(qty_delivered=1)
            Createareturnforthedelivery
            Validatereturnfordelivery(ingoing)(qty_delivered=0)
        """
        main_kit_product=self.env['product.product'].create({
            'name':'MainKit',
            'type':'product',
        })

        nested_kit_product=self.env['product.product'].create({
            'name':'NestedKit',
            'type':'product',
        })

        product=self.env['product.product'].create({
            'name':'Screw',
            'type':'product',
        })

        nested_kit_bom=self.env['mrp.bom'].create({
            'product_id':nested_kit_product.id,
            'product_tmpl_id':nested_kit_product.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(5,0),(0,0,{'product_id':product.id})]
        })

        main_bom=self.env['mrp.bom'].create({
            'product_id':main_kit_product.id,
            'product_tmpl_id':main_kit_product.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(5,0),(0,0,{'product_id':nested_kit_product.id})]
        })

        #CreateaSOforproductMainKitProduct
        order_form=Form(self.env['sale.order'])
        order_form.partner_id=self.env.ref('base.res_partner_2')
        withorder_form.order_line.new()asline:
            line.product_id=main_kit_product
            line.product_uom_qty=1
        order=order_form.save()
        order.action_confirm()
        qty_del_not_yet_validated=sum(sol.qty_deliveredforsolinorder.order_line)
        self.assertEqual(qty_del_not_yet_validated,0.0,'Nodeliveryvalidatedyet')

        #Validatedelivery
        pick=order.picking_ids
        pick.move_lines.write({'quantity_done':1})
        pick.button_validate()
        qty_del_validated=sum(sol.qty_deliveredforsolinorder.order_line)
        self.assertEqual(qty_del_validated,1.0,'Theorderwentfromwarehousetoclient,soithasbeendelivered')

        #1wasdelivered,nowcreateareturn
        stock_return_picking_form=Form(self.env['stock.return.picking'].with_context(
            active_ids=pick.ids,active_id=pick.ids[0],active_model='stock.picking'))
        return_wiz=stock_return_picking_form.save()
        forreturn_moveinreturn_wiz.product_return_moves:
            return_move.write({
                'quantity':1,
                'to_refund':True
            })
        res=return_wiz.create_returns()
        return_pick=self.env['stock.picking'].browse(res['res_id'])
        return_pick.move_line_ids.qty_done=1
        wiz_act=return_pick.button_validate() #validatereturn

        #Deliveredquantitiestotheclientshouldbe0
        qty_del_return_validated=sum(sol.qty_deliveredforsolinorder.order_line)
        self.assertNotEqual(qty_del_return_validated,1.0,"Thereturnwasvalidated,thereforethedeliveryfromclientto"
                                                           "companywassuccessful,andtheclientisleftwithouthis1product.")
        self.assertEqual(qty_del_return_validated,0.0,"Thereturnhasprocessed,clientdoesn'thaveanyquantityanymore")

    deftest_14_change_bom_type(self):
        """ThistestensuresthatupdatingaBomtypeduringaflowdoesnotleadtoanyerror"""
        p1=self._cls_create_product('Master',self.uom_unit)
        p2=self._cls_create_product('Component',self.uom_unit)
        p3=self.component_a
        p1.categ_id.write({
            'property_cost_method':'average',
            'property_valuation':'real_time',
        })
        stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.env['stock.quant']._update_available_quantity(self.component_a,stock_location,1)

        self.env['mrp.bom'].create({
            'product_tmpl_id':p1.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(0,0,{
                'product_id':p2.id,
                'product_qty':1.0,
            })]
        })

        p2_bom=self.env['mrp.bom'].create({
            'product_tmpl_id':p2.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(0,0,{
                'product_id':p3.id,
                'product_qty':1.0,
            })]
        })

        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'SuperPartner'})
        withso_form.order_line.new()asso_line:
            so_line.product_id=p1
        so=so_form.save()
        so.action_confirm()

        wiz_act=so.picking_ids.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        p2_bom.type="normal"

        so._create_invoices()
        invoice=so.invoice_ids
        invoice.action_post()
        self.assertEqual(invoice.state,'posted')

    deftest_15_anglo_saxon_variant_price_unit(self):
        """
        Testthepriceunitofavariantfromwhichtemplatehasanothervariantwithkitbom.
        Products:
            TemplateA
                variantNOKIT
                variantKIT:
                    ComponentA
        BusinessFlow:
            createproductsandkit
            createSOsellingbothvariants
            validatethedelivery
            createtheinvoice
            posttheinvoice
        """

        #Createenvironment
        self.env.company.currency_id=self.env.ref('base.USD')
        self.env.company.anglo_saxon_accounting=True
        self.partner=self.env.ref('base.res_partner_1')
        self.category=self.env.ref('product.product_category_1').copy({'name':'Testcategory','property_valuation':'real_time','property_cost_method':'fifo'})
        account_type=self.env['account.account.type'].create({'name':'RCVtype','type':'other','internal_group':'asset'})
        account_receiv=self.env['account.account'].create({'name':'Receivable','code':'RCV00','user_type_id':account_type.id,'reconcile':True})
        account_expense=self.env['account.account'].create({'name':'Expense','code':'EXP00','user_type_id':account_type.id,'reconcile':True})
        account_output=self.env['account.account'].create({'name':'Output','code':'OUT00','user_type_id':account_type.id,'reconcile':True})
        account_valuation=self.env['account.account'].create({'name':'Valuation','code':'STV00','user_type_id':account_type.id,'reconcile':True})
        self.stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.partner.property_account_receivable_id=account_receiv
        self.category.property_account_income_categ_id=account_receiv
        self.category.property_account_expense_categ_id=account_expense
        self.category.property_stock_account_input_categ_id=account_receiv
        self.category.property_stock_account_output_categ_id=account_output
        self.category.property_stock_valuation_account_id=account_valuation

        #Createvariantattributes
        self.prod_att_test=self.env['product.attribute'].create({'name':'test'})
        self.prod_attr_KIT=self.env['product.attribute.value'].create({'name':'KIT','attribute_id':self.prod_att_test.id,'sequence':1})
        self.prod_attr_NOKIT=self.env['product.attribute.value'].create({'name':'NOKIT','attribute_id':self.prod_att_test.id,'sequence':2})

        #Createthetemplate
        self.product_template=self.env['product.template'].create({
            'name':'TemplateA',
            'type':'product',
            'uom_id':self.uom_unit.id,
            'invoice_policy':'delivery',
            'categ_id':self.category.id,
            'attribute_line_ids':[(0,0,{
                'attribute_id':self.prod_att_test.id,
                'value_ids':[(6,0,[self.prod_attr_KIT.id,self.prod_attr_NOKIT.id])]
            })]
        })

        #Createthevariants
        self.pt_attr_KIT=self.product_template.attribute_line_ids[0].product_template_value_ids[0]
        self.pt_attr_NOKIT=self.product_template.attribute_line_ids[0].product_template_value_ids[1]
        self.variant_KIT=self.product_template._get_variant_for_combination(self.pt_attr_KIT)
        self.variant_NOKIT=self.product_template._get_variant_for_combination(self.pt_attr_NOKIT)
        #AssignacosttotheNOKITvariant
        self.variant_NOKIT.write({'standard_price':25})

        #Createthecomponents
        self.comp_kit_a=self.env['product.product'].create({
            'name':'ComponentKitA',
            'type':'product',
            'uom_id':self.uom_unit.id,
            'categ_id':self.category.id,
            'standard_price':20
        })
        self.comp_kit_b=self.env['product.product'].create({
            'name':'ComponentKitB',
            'type':'product',
            'uom_id':self.uom_unit.id,
            'categ_id':self.category.id,
            'standard_price':10
        })

        #Createthebom
        bom=self.env['mrp.bom'].create({
            'product_tmpl_id':self.product_template.id,
            'product_id':self.variant_KIT.id,
            'product_qty':1.0,
            'type':'phantom'
        })
        self.env['mrp.bom.line'].create({
            'product_id':self.comp_kit_a.id,
            'product_qty':2.0,
            'bom_id':bom.id
        })
        self.env['mrp.bom.line'].create({
            'product_id':self.comp_kit_b.id,
            'product_qty':1.0,
            'bom_id':bom.id
        })

        #Createthequants
        self.env['stock.quant']._update_available_quantity(self.variant_KIT,self.stock_location,1)
        self.env['stock.quant']._update_available_quantity(self.comp_kit_a,self.stock_location,2)
        self.env['stock.quant']._update_available_quantity(self.comp_kit_b,self.stock_location,1)
        self.env['stock.quant']._update_available_quantity(self.variant_NOKIT,self.stock_location,1)

        #Createthesaleorder
        so_vals={
            'partner_id':self.partner.id,
            'partner_invoice_id':self.partner.id,
            'partner_shipping_id':self.partner.id,
            'order_line':[(0,0,{
                'name':self.variant_KIT.name,
                'product_id':self.variant_KIT.id,
                'product_uom_qty':1,
                'product_uom':self.uom_unit.id,
                'price_unit':100,
            }),(0,0,{
                'name':self.variant_NOKIT.name,
                'product_id':self.variant_NOKIT.id,
                'product_uom_qty':1,
                'product_uom':self.uom_unit.id,
                'price_unit':50
            })],
            'pricelist_id':self.env.ref('product.list0').id,
            'company_id':self.env.company.id
        }
        so=self.env['sale.order'].create(so_vals)
        #Validatethesaleorder
        so.action_confirm()
        #Delivertheproducts
        pick=so.picking_ids
        wiz_act=pick.button_validate()
        Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save().process()
        #Createtheinvoice
        so._create_invoices()
        #Validatetheinvoice
        invoice=so.invoice_ids
        invoice.action_post()

        amls=invoice.line_ids
        aml_kit_expense=amls.filtered(lambdal:l.is_anglo_saxon_lineandl.debit>0andl.product_id==self.variant_KIT)
        aml_kit_output=amls.filtered(lambdal:l.is_anglo_saxon_lineandl.credit>0andl.product_id==self.variant_KIT)
        aml_nokit_expense=amls.filtered(lambdal:l.is_anglo_saxon_lineandl.debit>0andl.product_id==self.variant_NOKIT)
        aml_nokit_output=amls.filtered(lambdal:l.is_anglo_saxon_lineandl.credit>0andl.product_id==self.variant_NOKIT)

        #CheckthattheCostofGoodsSoldforvariantKITisequalto(2*20)+10=50
        self.assertEqual(aml_kit_expense.debit,50,"CostofGoodSoldentrymissingormismatchingforvariantwithkit")
        self.assertEqual(aml_kit_output.credit,50,"CostofGoodSoldentrymissingormismatchingforvariantwithkit")
        #CheckthattheCostofGoodsSoldforvariantNOKITisequaltoitsstandard_price=25
        self.assertEqual(aml_nokit_expense.debit,25,"CostofGoodSoldentrymissingormismatchingforvariantwithoutkit")
        self.assertEqual(aml_nokit_output.credit,25,"CostofGoodSoldentrymissingormismatchingforvariantwithoutkit")

    deftest_reconfirm_cancelled_kit(self):
        so=self.env['sale.order'].create({
            'partner_id':self.env.ref('base.res_partner_1').id,
            'order_line':[
                (0,0,{
                    'name':self.kit_1.name,
                    'product_id':self.kit_1.id,
                    'product_uom_qty':1.0,
                    'price_unit':1.0,
                })
            ],
        })

        #Updatingthequantitiesinstocktopreventa'Notenoughinventory'warningmessage.
        stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.env['stock.quant']._update_available_quantity(self.component_a,stock_location,10)
        self.env['stock.quant']._update_available_quantity(self.component_b,stock_location,10)
        self.env['stock.quant']._update_available_quantity(self.component_c,stock_location,10)

        so.action_confirm()
        #Checkpickingcreation
        self.assertEqual(len(so.picking_ids),1,"ApickingshouldbecreatedaftertheSOvalidation")

        wiz_act=so.picking_ids.button_validate()
        wiz=Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        so.action_cancel()
        so.action_draft()
        so.action_confirm()
        self.assertEqual(len(so.picking_ids),1,"Theproductwasalreadydelivered,noneedtore-createadeliveryorder")

    deftest_anglo_saxo_return_and_credit_note(self):
        """
        Whenpostingacreditnoteforareturnedkit,thevalueoftheanglo-saxolines
        shouldbebasedonthereturnedcomponent'svalue
        """
        stock_input_account,stock_output_account,stock_valuation_account,expense_account,stock_journal=_create_accounting_data(self.env)
        fifo=self.env['product.category'].create({
            'name':'FIFO',
            'property_valuation':'real_time',
            'property_cost_method':'fifo',
            'property_stock_account_input_categ_id':stock_input_account.id,
            'property_stock_account_output_categ_id':stock_output_account.id,
            'property_stock_valuation_account_id':stock_valuation_account.id,
            'property_stock_journal':stock_journal.id,
        })

        kit=self._create_product('SimpleKit',self.uom_unit)
        (kit+self.component_a).categ_id=fifo
        kit.property_account_expense_id=expense_account

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(0,0,{'product_id':self.component_a.id,'product_qty':1.0})]
        })

        #Receive3components:one@10,one@20andone@60
        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.component_a.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.component_a.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpin[10,20,60]])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Sell3kits
        so=self.env['sale.order'].create({
            'partner_id':self.env.ref('base.res_partner_1').id,
            'order_line':[
                (0,0,{
                    'name':kit.name,
                    'product_id':kit.id,
                    'product_uom_qty':3.0,
                    'product_uom':kit.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        #Deliverthecomponents:1@10,then1@20andthen1@60
        pickings=[]
        picking=so.picking_ids
        whilepicking:
            pickings.append(picking)
            picking.move_lines.quantity_done=1
            action=picking.button_validate()
            ifisinstance(action,dict):
                wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
                wizard.process()
            picking=picking.backorder_ids

        invoice=so._create_invoices()
        invoice.action_post()

        #Receiveone@100
        in_moves=self.env['stock.move'].create({
            'name':'INmove@100',
            'product_id':self.component_a.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.component_a.uom_id.id,
            'product_uom_qty':1,
            'price_unit':100,
        })
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Returnthesecondpicking(i.e.onecomponent@20)
        ctx={'active_id':pickings[1].id,'active_model':'stock.picking'}
        return_wizard=Form(self.env['stock.return.picking'].with_context(ctx)).save()
        return_picking_id,dummy=return_wizard._create_returns()
        return_picking=self.env['stock.picking'].browse(return_picking_id)
        return_picking.move_lines.quantity_done=1
        return_picking.button_validate()

        #Addacreditnoteforthereturnedkit
        ctx={'active_model':'account.move','active_ids':invoice.ids}
        refund_wizard=self.env['account.move.reversal'].with_context(ctx).create({'refund_method':'refund'})
        action=refund_wizard.reverse_moves()
        reverse_invoice=self.env['account.move'].browse(action['res_id'])
        withForm(reverse_invoice)asreverse_invoice_form:
            withreverse_invoice_form.invoice_line_ids.edit(0)asline:
                line.quantity=1
        reverse_invoice.action_post()

        amls=reverse_invoice.line_ids
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==stock_output_account)
        self.assertEqual(stock_out_aml.debit,20,'Shouldbetothevalueofthereturnedcomponent')
        self.assertEqual(stock_out_aml.credit,0)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==expense_account)
        self.assertEqual(cogs_aml.debit,0)
        self.assertEqual(cogs_aml.credit,20,'Shouldbetothevalueofthereturnedcomponent')

    deftest_anglo_saxo_return_and_create_invoice(self):
        """
        Whencreatinganinvoiceforareturnedkit,thevalueoftheanglo-saxolines
        shouldbebasedonthereturnedcomponent'svalue
        """
        stock_input_account,stock_output_account,stock_valuation_account,expense_account,stock_journal=_create_accounting_data(self.env)
        fifo=self.env['product.category'].create({
            'name':'FIFO',
            'property_valuation':'real_time',
            'property_cost_method':'fifo',
            'property_stock_account_input_categ_id':stock_input_account.id,
            'property_stock_account_output_categ_id':stock_output_account.id,
            'property_stock_valuation_account_id':stock_valuation_account.id,
            'property_stock_journal':stock_journal.id,
        })

        kit=self._create_product('SimpleKit',self.uom_unit)
        (kit+self.component_a).categ_id=fifo
        kit.property_account_expense_id=expense_account

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(0,0,{'product_id':self.component_a.id,'product_qty':1.0})]
        })

        #Receive3components:one@10,one@20andone@60
        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.component_a.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.component_a.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpin[10,20,60]])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Sell3kits
        so=self.env['sale.order'].create({
            'partner_id':self.env.ref('base.res_partner_1').id,
            'order_line':[
                (0,0,{
                    'name':kit.name,
                    'product_id':kit.id,
                    'product_uom_qty':3.0,
                    'product_uom':kit.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        #Deliverthecomponents:1@10,then1@20andthen1@60
        pickings=[]
        picking=so.picking_ids
        whilepicking:
            pickings.append(picking)
            picking.move_lines.quantity_done=1
            action=picking.button_validate()
            ifisinstance(action,dict):
                wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
                wizard.process()
            picking=picking.backorder_ids

        invoice=so._create_invoices()
        invoice.action_post()

        #Receiveone@100
        in_moves=self.env['stock.move'].create({
            'name':'INmove@100',
            'product_id':self.component_a.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.component_a.uom_id.id,
            'product_uom_qty':1,
            'price_unit':100,
        })
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        #Returnthesecondpicking(i.e.onecomponent@20)
        ctx={'active_id':pickings[1].id,'active_model':'stock.picking'}
        return_wizard=Form(self.env['stock.return.picking'].with_context(ctx)).save()
        return_picking_id,dummy=return_wizard._create_returns()
        return_picking=self.env['stock.picking'].browse(return_picking_id)
        return_picking.move_lines.quantity_done=1
        return_picking.button_validate()

        #Createanewinvoiceforthereturnedkit
        ctx={'active_model':'sale.order','active_ids':so.ids}
        create_invoice_wizard=self.env['sale.advance.payment.inv'].with_context(ctx).create({'advance_payment_method':'delivered'})
        create_invoice_wizard.create_invoices()
        reverse_invoice=so.invoice_ids[-1]
        withForm(reverse_invoice)asreverse_invoice_form:
            withreverse_invoice_form.invoice_line_ids.edit(0)asline:
                line.quantity=1
        reverse_invoice.action_post()

        amls=reverse_invoice.line_ids
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==stock_output_account)
        self.assertEqual(stock_out_aml.debit,20,'Shouldbetothevalueofthereturnedcomponent')
        self.assertEqual(stock_out_aml.credit,0)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==expense_account)
        self.assertEqual(cogs_aml.debit,0)
        self.assertEqual(cogs_aml.credit,20,'Shouldbetothevalueofthereturnedcomponent')

    deftest_kit_margin_and_return_picking(self):
        """Thistestensurethat,whenreturningthecomponentsofasoldkit,the
        saleorderlinecostdoesnotchange"""
        kit=self._cls_create_product('SuperKit',self.uom_unit)
        (kit+self.component_a).categ_id.property_cost_method='fifo'

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(0,0,{
                'product_id':self.component_a.id,
                'product_qty':1.0,
            })]
        })

        self.component_a.standard_price=10
        kit.button_bom_cost()

        stock_location=self.company_data['default_warehouse'].lot_stock_id
        self.env['stock.quant']._update_available_quantity(self.component_a,stock_location,1)

        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.partner_a
        withso_form.order_line.new()asline:
            line.product_id=kit
        so=so_form.save()
        so.action_confirm()

        line=so.order_line
        price=line.product_id.with_company(line.company_id)._compute_average_price(0,line.product_uom_qty,line.move_ids)
        self.assertEqual(price,10)

        picking=so.picking_ids
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()

        ctx={'active_ids':picking.ids,'active_id':picking.ids[0],'active_model':'stock.picking'}
        return_picking_wizard_form=Form(self.env['stock.return.picking'].with_context(ctx))
        return_picking_wizard=return_picking_wizard_form.save()
        return_picking_wizard.create_returns()

        price=line.product_id.with_company(line.company_id)._compute_average_price(0,line.product_uom_qty,line.move_ids)
        self.assertEqual(price,10)

    deftest_fifo_reverse_and_create_new_invoice(self):
        """
        FIFOautomated
        Kitwithonecomponent
        Receivethecomponent:1@10,1@50
        Deliver1kit
        Posttheinvoice,addacreditnotewithoption'newdraftinv'
        Postthesecondinvoice
        COGSshouldbebasedonthedeliveredkit
        """
        kit=self._create_product('SimpleKit',self.uom_unit)
        categ_form=Form(self.env['product.category'])
        categ_form.name='SuperFifo'
        categ_form.property_cost_method='fifo'
        categ_form.property_valuation='real_time'
        categ=categ_form.save()
        (kit+self.component_a).categ_id=categ

        self.env['mrp.bom'].create({
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[(0,0,{'product_id':self.component_a.id,'product_qty':1.0})]
        })

        in_moves=self.env['stock.move'].create([{
            'name':'INmove@%s'%p,
            'product_id':self.component_a.id,
            'location_id':self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id':self.company_data['default_warehouse'].lot_stock_id.id,
            'product_uom':self.component_a.uom_id.id,
            'product_uom_qty':1,
            'price_unit':p,
        }forpin[10,50]])
        in_moves._action_confirm()
        in_moves.quantity_done=1
        in_moves._action_done()

        so=self.env['sale.order'].create({
            'partner_id':self.env.ref('base.res_partner_1').id,
            'order_line':[
                (0,0,{
                    'name':kit.name,
                    'product_id':kit.id,
                    'product_uom_qty':1.0,
                    'product_uom':kit.uom_id.id,
                    'price_unit':100,
                    'tax_id':False,
                })],
        })
        so.action_confirm()

        picking=so.picking_ids
        picking.move_lines.quantity_done=1.0
        picking.button_validate()

        invoice01=so._create_invoices()
        invoice01.action_post()

        wizard=self.env['account.move.reversal'].with_context(active_model="account.move",active_ids=invoice01.ids).create({
            'refund_method':'modify',
        })
        invoice02=self.env['account.move'].browse(wizard.reverse_moves()['res_id'])
        invoice02.action_post()

        amls=invoice02.line_ids
        stock_out_aml=amls.filtered(lambdaaml:aml.account_id==categ.property_stock_account_output_categ_id)
        self.assertEqual(stock_out_aml.debit,0)
        self.assertEqual(stock_out_aml.credit,10)
        cogs_aml=amls.filtered(lambdaaml:aml.account_id==categ.property_account_expense_categ_id)
        self.assertEqual(cogs_aml.debit,10)
        self.assertEqual(cogs_aml.credit,0)

    deftest_kit_avco_fully_owned_and_delivered_invoice_post_delivery(self):
        self.stock_account_product_categ.property_cost_method='average'

        compo01,compo02,kit=self.env['product.product'].create([{
            'name':name,
            'type':'product',
            'standard_price':price,
            'categ_id':self.stock_account_product_categ.id,
            'invoice_policy':'delivery',
        }forname,pricein[
            ('Compo01',10),
            ('Compo02',20),
            ('Kit',0),
        ]])

        self.env['stock.quant']._update_available_quantity(compo01,self.company_data['default_warehouse'].lot_stock_id,1,owner_id=self.partner_b)
        self.env['stock.quant']._update_available_quantity(compo02,self.company_data['default_warehouse'].lot_stock_id,1,owner_id=self.partner_b)

        self.env['mrp.bom'].create({
            'product_id':kit.id,
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_uom_id':kit.uom_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo01.id,'product_qty':1.0}),
                (0,0,{'product_id':compo02.id,'product_qty':1.0}),
            ],
        })

        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':kit.name,
                    'product_id':kit.id,
                    'product_uom_qty':1.0,
                    'product_uom':kit.uom_id.id,
                    'price_unit':5,
                    'tax_id':False,
                })],
        })
        so.action_confirm()
        so.picking_ids.move_lines.quantity_done=1
        so.picking_ids.button_validate()

        invoice=so._create_invoices()
        invoice.action_post()

        #COGSshouldnotexistbecausetheproductsareownedbyanexternalpartner
        amls=invoice.line_ids
        self.assertRecordValues(amls,[
            #pylint:disable=bad-whitespace
            {'account_id':self.company_data['default_account_revenue'].id,    'debit':0,    'credit':5},
            {'account_id':self.company_data['default_account_receivable'].id, 'debit':5,    'credit':0},
        ])

    deftest_kit_avco_partially_owned_and_delivered_invoice_post_delivery(self):
        self.stock_account_product_categ.property_cost_method='average'

        compo01,compo02,kit=self.env['product.product'].create([{
            'name':name,
            'type':'product',
            'standard_price':price,
            'categ_id':self.stock_account_product_categ.id,
            'invoice_policy':'delivery',
        }forname,pricein[
            ('Compo01',10),
            ('Compo02',20),
            ('Kit',0),
        ]])

        self.env['stock.quant']._update_available_quantity(compo01,self.company_data['default_warehouse'].lot_stock_id,1,owner_id=self.partner_b)
        self.env['stock.quant']._update_available_quantity(compo01,self.company_data['default_warehouse'].lot_stock_id,1)
        self.env['stock.quant']._update_available_quantity(compo02,self.company_data['default_warehouse'].lot_stock_id,1,owner_id=self.partner_b)
        self.env['stock.quant']._update_available_quantity(compo02,self.company_data['default_warehouse'].lot_stock_id,1)

        self.env['mrp.bom'].create({
            'product_id':kit.id,
            'product_tmpl_id':kit.product_tmpl_id.id,
            'product_uom_id':kit.uom_id.id,
            'product_qty':1.0,
            'type':'phantom',
            'bom_line_ids':[
                (0,0,{'product_id':compo01.id,'product_qty':1.0}),
                (0,0,{'product_id':compo02.id,'product_qty':1.0}),
            ],
        })

        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':kit.name,
                    'product_id':kit.id,
                    'product_uom_qty':2.0,
                    'product_uom':kit.uom_id.id,
                    'price_unit':5,
                    'tax_id':False,
                })],
        })
        so.action_confirm()
        so.picking_ids.move_line_ids.qty_done=1
        so.picking_ids.button_validate()

        invoice=so._create_invoices()
        invoice.action_post()

        #COGSshouldnotexistbecausetheproductsareownedbyanexternalpartner
        amls=invoice.line_ids
        self.assertRecordValues(amls,[
            #pylint:disable=bad-whitespace
            {'account_id':self.company_data['default_account_revenue'].id,    'debit':0,    'credit':10},
            {'account_id':self.company_data['default_account_receivable'].id, 'debit':10,   'credit':0},
            {'account_id':self.company_data['default_account_stock_out'].id,  'debit':0,    'credit':30},
            {'account_id':self.company_data['default_account_expense'].id,    'debit':30,   'credit':0},
        ])

    deftest_avoid_removing_kit_bom_in_use(self):
        so=self.env['sale.order'].create({
            'partner_id':self.partner_a.id,
            'order_line':[
                (0,0,{
                    'name':self.kit_1.name,
                    'product_id':self.kit_1.id,
                    'product_uom_qty':1.0,
                    'product_uom':self.kit_1.uom_id.id,
                    'price_unit':5,
                    'tax_id':False,
                })],
        })
        self.bom_kit_1.toggle_active()
        self.bom_kit_1.toggle_active()

        so.action_confirm()
        withself.assertRaises(UserError):
            self.bom_kit_1.toggle_active()
        withself.assertRaises(UserError):
            self.bom_kit_1.unlink()

        formoveinso.order_line.move_ids:
            move.quantity_done=move.product_uom_qty
        so.picking_ids.button_validate()

        self.assertEqual(so.picking_ids.state,'done')
        withself.assertRaises(UserError):
            self.bom_kit_1.toggle_active()
        withself.assertRaises(UserError):
            self.bom_kit_1.unlink()

        invoice=so._create_invoices()
        invoice.action_post()

        self.assertEqual(invoice.state,'posted')
        self.bom_kit_1.toggle_active()
        self.bom_kit_1.toggle_active()
        self.bom_kit_1.unlink()
