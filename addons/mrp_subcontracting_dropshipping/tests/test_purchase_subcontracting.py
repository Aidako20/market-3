#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.addons.mrp_subcontracting.tests.commonimportTestMrpSubcontractingCommon


classTestSubcontractingDropshippingFlows(TestMrpSubcontractingCommon):

    deftest_mrp_subcontracting_dropshipping_1(self):
        """Markthesubcontractedproductwiththeroutedropshipandaddthe
        subcontractorasseller.Thecomponenthastheroutes'MTO','Replenish
        onorder'and'Buy'.Alsoanotherpartnerissetasvendoronthecomp.
        CreateaSOandcheckthat:
        -Deliverybetweensubcontractorandcustomerforsubcontractedproduct.
        -Deliveryforthecomponenttothesubcontractorforthespecifiedwh.
        -Pocreatedforthecomponent.
        """
        self.env.ref('stock.route_warehouse0_mto').active=True
        mto_route=self.env['stock.location.route'].search([('name','=','ReplenishonOrder(MTO)')])
        resupply_route=self.env['stock.location.route'].search([('name','=','ResupplySubcontractoronOrder')])
        buy_route=self.env['stock.location.route'].search([('name','=','Buy')])
        dropship_route=self.env['stock.location.route'].search([('name','=','Dropship')])
        self.comp2.write({'route_ids':[(4,buy_route.id),(4,mto_route.id),(4,resupply_route.id)]})
        self.finished.write({'route_ids':[(4,dropship_route.id)]})

        warehouse=self.env['stock.warehouse'].create({
            'name':'WarehouseForsubcontract',
            'code':'WFS'
        })

        self.env['product.supplierinfo'].create({
            'product_tmpl_id':self.finished.product_tmpl_id.id,
            'name':self.subcontractor_partner1.id
        })

        partner=self.env['res.partner'].create({
            'name':'Toto'
        })
        self.env['product.supplierinfo'].create({
            'product_tmpl_id':self.comp2.product_tmpl_id.id,
            'name':partner.id
        })

        #Createareceiptpickingfromthesubcontractor
        so_form=Form(self.env['sale.order'])
        so_form.partner_id=partner
        so_form.warehouse_id=warehouse
        withso_form.order_line.new()asline:
            line.product_id=self.finished
            line.product_uom_qty=1
        so=so_form.save()
        so.action_confirm()

        #Pickingsshoulddirectlybecreated
        po=self.env['purchase.order'].search([('origin','ilike',so.name)])
        self.assertTrue(po)

        po.button_approve()

        picking_finished=po.picking_ids
        self.assertEqual(len(picking_finished),1.0)
        self.assertEqual(picking_finished.location_dest_id,partner.property_stock_customer)
        self.assertEqual(picking_finished.location_id,self.subcontractor_partner1.property_stock_supplier)
        self.assertEqual(picking_finished.state,'assigned')

        picking_delivery=self.env['stock.move'].search([
            ('product_id','=',self.comp2.id),
            ('location_id','=',warehouse.lot_stock_id.id),
            ('location_dest_id','=',self.subcontractor_partner1.property_stock_subcontractor.id),
        ]).picking_id
        self.assertTrue(picking_delivery)
        self.assertEqual(picking_delivery.state,'waiting')

        po=self.env['purchase.order.line'].search([
            ('product_id','=',self.comp2.id),
            ('partner_id','=',partner.id),
        ]).order_id
        self.assertTrue(po)

    deftest_mrp_subcontracting_purchase_2(self):
        """Let'sconsiderasubcontractedBOMwith1component.Tick"ResupplySubcontractoronOrder"onthecomponentandsetasupplieronit.
        Purchase1BOMtothesubcontractor.Confirmthepurchaseandchangethepurchasedquantityto2.
        Checkthat2componentsaredeliveredtothesubcontractor
        """
        #Tick"resupplysubconractoronorderoncomponent"
        self.bom.bom_line_ids=[(5,0,0)]
        self.bom.bom_line_ids=[(0,0,{'product_id':self.comp1.id,'product_qty':1})]
        resupply_sub_on_order_route=self.env['stock.location.route'].search([('name','=','ResupplySubcontractoronOrder')])
        (self.comp1).write({'route_ids':[(4,resupply_sub_on_order_route.id,None)]})
        #Createasupplierandsetittocomponent
        vendor=self.env['res.partner'].create({'name':'AAA','email':'from.test@example.com'})
        supplier_info1=self.env['product.supplierinfo'].create({
            'name':vendor.id,
            'price':50,
        })
        self.comp1.write({'seller_ids':[(0,0,{'name':vendor.id,'product_code':'COMP1'})]})
        #Purchase1BOMtothesubcontractor
        po=Form(self.env['purchase.order'])
        po.partner_id=self.subcontractor_partner1
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.finished
            po_line.product_qty=1
            po_line.price_unit=100
        po=po.save()
        #Confirmthepurchase
        po.button_confirm()
        #Checkonedeliveryorderwiththecomponenthasbeencreatedforthesubcontractor
        mo=self.env['mrp.production'].search([('bom_id','=',self.bom.id)])
        self.assertEqual(mo.state,'confirmed')
        #Checkthat1deliverywith1componentforthesubcontractorhasbeencreated
        picking_delivery=mo.picking_ids
        wh=picking_delivery.picking_type_id.warehouse_id
        origin=picking_delivery.origin
        self.assertEqual(len(picking_delivery),1)
        self.assertEqual(len(picking_delivery.move_ids_without_package),1)
        self.assertEqual(picking_delivery.picking_type_id,wh.out_type_id)
        self.assertEqual(picking_delivery.partner_id,self.subcontractor_partner1)

        #Changethepurchasedquantityto2
        po.order_line.write({'product_qty':2})
        #Checkthattwodeliverieswith1componentforthesubcontractorhavebeencreated
        picking_deliveries=self.env['stock.picking'].search([('origin','=',origin)])
        self.assertEqual(len(picking_deliveries),2)
        self.assertEqual(picking_deliveries[0].picking_type_id,wh.out_type_id)
        self.assertEqual(picking_deliveries[0].partner_id,self.subcontractor_partner1)
        self.assertTrue(picking_deliveries[0].state!='cancel')
        move1=picking_deliveries[0].move_ids_without_package
        self.assertEqual(picking_deliveries[1].picking_type_id,wh.out_type_id)
        self.assertEqual(picking_deliveries[1].partner_id,self.subcontractor_partner1)
        self.assertTrue(picking_deliveries[1].state!='cancel')
        move2=picking_deliveries[1].move_ids_without_package
        self.assertEqual(move1.product_id,self.comp1)
        self.assertEqual(move1.product_uom_qty,1)
        self.assertEqual(move2.product_id,self.comp1)
        self.assertEqual(move2.product_uom_qty,1)

    deftest_po_to_customer(self):
        """
        CreateandconfirmaPOwithasubcontractedmove.Thepickingtypeof
        thePOis'Dropship'andthedeliveryaddressacustomer.Then,process
        areturnwiththestocklocationasdestinationandanotherreturnwith
        thesupplierasdestination
        """
        subcontractor,client=self.env['res.partner'].create([
            {'name':'SuperSubcontractor'},
            {'name':'SuperClient'},
        ])

        p_finished,p_compo=self.env['product.product'].create([{
            'name':'FinishedProduct',
            'type':'product',
            'seller_ids':[(0,0,{'name':subcontractor.id})],
        },{
            'name':'Component',
            'type':'consu',
        }])

        bom=self.env['mrp.bom'].create({
            'product_tmpl_id':p_finished.product_tmpl_id.id,
            'product_qty':1,
            'type':'subcontract',
            'subcontractor_ids':[(6,0,subcontractor.ids)],
            'bom_line_ids':[
                (0,0,{'product_id':p_compo.id,'product_qty':1}),
            ],
        })

        dropship_picking_type=self.env['stock.picking.type'].search([
            ('company_id','=',self.env.company.id),
            ('default_location_src_id.usage','=','supplier'),
            ('default_location_dest_id.usage','=','customer'),
        ],limit=1,order='sequence')

        po=self.env['purchase.order'].create({
            "partner_id":subcontractor.id,
            "picking_type_id":dropship_picking_type.id,
            "dest_address_id":client.id,
            "order_line":[(0,0,{
                'product_id':p_finished.id,
                'name':p_finished.name,
                'product_qty':2.0,
            })],
        })
        po.button_confirm()

        mo=self.env['mrp.production'].search([('bom_id','=',bom.id)])
        self.assertEqual(mo.picking_type_id,self.warehouse.subcontracting_type_id)

        delivery=po.picking_ids
        delivery.move_line_ids.qty_done=2.0
        delivery.button_validate()

        self.assertEqual(delivery.state,'done')
        self.assertEqual(mo.state,'done')
        self.assertEqual(po.order_line.qty_received,2)

        #return1xP_finishedtothestocklocation
        stock_location=self.warehouse.lot_stock_id
        stock_location.return_location=True
        return_form=Form(self.env['stock.return.picking'].with_context(active_ids=delivery.ids,active_id=delivery.id,active_model='stock.picking'))
        withreturn_form.product_return_moves.edit(0)asline:
            line.quantity=1.0
        return_form.location_id=stock_location
        return_wizard=return_form.save()
        return_picking_id,_pick_type_id=return_wizard._create_returns()

        delivery_return01=self.env['stock.picking'].browse(return_picking_id)
        delivery_return01.move_line_ids.qty_done=1.0
        delivery_return01.button_validate()

        self.assertEqual(delivery_return01.state,'done')
        self.assertEqual(p_finished.qty_available,1,'Oneproducthasbeenreturnedtothestocklocation,soitshouldbeavailable')
        self.assertEqual(po.order_line.qty_received,2,'Oneproducthasbeenreturnedtothestocklocation,soweshouldstillconsideritasreceived')

        #return1xP_finishedtothesupplierlocation
        supplier_location=dropship_picking_type.default_location_src_id
        return_form=Form(self.env['stock.return.picking'].with_context(active_ids=delivery.ids,active_id=delivery.id,active_model='stock.picking'))
        withreturn_form.product_return_moves.edit(0)asline:
            line.quantity=1.0
        return_form.location_id=supplier_location
        return_wizard=return_form.save()
        return_picking_id,_pick_type_id=return_wizard._create_returns()

        delivery_return02=self.env['stock.picking'].browse(return_picking_id)
        delivery_return02.move_line_ids.qty_done=1.0
        delivery_return02.button_validate()

        self.assertEqual(delivery_return02.state,'done')
        self.assertEqual(po.order_line.qty_received,1)

    deftest_po_to_subcontractor(self):
        """
        CreateandconfirmaPOwithasubcontractedmove.Theboughtproductis
        alsoacomponentofanothersubcontractedproduct.Thepickingtypeof
        thePOis'Dropship'andthedeliveryaddressistheothersubcontractor
        """
        subcontractor,super_subcontractor=self.env['res.partner'].create([
            {'name':'Subcontractor'},
            {'name':'SuperSubcontractor'},
        ])
        super_subcontractor.property_stock_customer=super_subcontractor.property_stock_subcontractor

        super_product,product,component=self.env['product.product'].create([{
            'name':'SuperProduct',
            'type':'product',
            'seller_ids':[(0,0,{'name':super_subcontractor.id})],
        },{
            'name':'Product',
            'type':'product',
            'seller_ids':[(0,0,{'name':subcontractor.id})],
        },{
            'name':'Component',
            'type':'consu',
        }])

        _,bom_product=self.env['mrp.bom'].create([{
            'product_tmpl_id':super_product.product_tmpl_id.id,
            'product_qty':1,
            'type':'subcontract',
            'subcontractor_ids':[(6,0,super_subcontractor.ids)],
            'bom_line_ids':[
                (0,0,{'product_id':product.id,'product_qty':1}),
            ],
        },{
            'product_tmpl_id':product.product_tmpl_id.id,
            'product_qty':1,
            'type':'subcontract',
            'subcontractor_ids':[(6,0,subcontractor.ids)],
            'bom_line_ids':[
                (0,0,{'product_id':component.id,'product_qty':1}),
            ],
        }])

        dropship_picking_type=self.env['stock.picking.type'].search([
            ('company_id','=',self.env.company.id),
            ('default_location_src_id.usage','=','supplier'),
            ('default_location_dest_id.usage','=','customer'),
        ],limit=1,order='sequence')

        po=self.env['purchase.order'].create({
            "partner_id":subcontractor.id,
            "picking_type_id":dropship_picking_type.id,
            "dest_address_id":super_subcontractor.id,
            "order_line":[(0,0,{
                'product_id':product.id,
                'name':product.name,
                'product_qty':1.0,
            })],
        })
        po.button_confirm()

        mo=self.env['mrp.production'].search([('bom_id','=',bom_product.id)])
        self.assertEqual(mo.picking_type_id,self.warehouse.subcontracting_type_id)

        delivery=po.picking_ids
        delivery.move_line_ids.qty_done=1.0
        delivery.button_validate()

        self.assertEqual(po.order_line.qty_received,1.0)
