#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestPackingNeg(TransactionCase):

    deftest_packing_neg(self):
        res_partner_2=self.env['res.partner'].create({
            'name':'DecoAddict',
            'email':'deco.addict82@example.com',
        })

        res_partner_4=self.env['res.partner'].create({
            'name':'ReadyMat',
            'email':'ready.mat28@example.com',
        })

        #Createanew"negative"storableproduct
        product_neg=self.env['product.product'].create({
            'name':'Negativeproduct',
            'type':'product',
            'categ_id':self.ref('product.product_category_1'),
            'list_price':100.0,
            'standard_price':70.0,
            'seller_ids':[(0,0,{
                'delay':1,
                'name':res_partner_2.id,
                'min_qty':2.0,})],
            'uom_id':self.ref('uom.product_uom_unit'),
            'uom_po_id':self.ref('uom.product_uom_unit'),
        })

        #Createanincomingpickingforthisproductof300PCEfromsupplierstostock
        vals={
            'name':'Incomingpicking(negativeproduct)',
            'partner_id':res_partner_2.id,
            'picking_type_id':self.ref('stock.picking_type_in'),
            'location_id':self.ref('stock.stock_location_suppliers'),
            'location_dest_id':self.ref('stock.stock_location_stock'),
            'move_lines':[(0,0,{
                'name':'NEG',
                'product_id':product_neg.id,
                'product_uom':product_neg.uom_id.id,
                'product_uom_qty':300.00,
                'location_id':self.ref('stock.stock_location_suppliers'),
                'location_dest_id':self.ref('stock.stock_location_stock'),
            })],
        }
        pick_neg=self.env['stock.picking'].create(vals)
        pick_neg.onchange_picking_type()
        pick_neg.move_lines.onchange_product_id()

        #Confirmandassignpicking
        pick_neg.action_confirm()
        pick_neg.action_assign()

        #Put120piecesonPalneg1(package),120piecesonPalneg2withlotAand60piecesonPalneg3
        #createlotA
        lot_a=self.env['stock.production.lot'].create({'name':'Lotneg','product_id':product_neg.id,'company_id':self.env.company.id})
        #createpackage
        package1=self.env['stock.quant.package'].create({'name':'Palneg1'})
        package2=self.env['stock.quant.package'].create({'name':'Palneg2'})
        package3=self.env['stock.quant.package'].create({'name':'Palneg3'})
        #Createpackageforeachlineandassignitasresult_package_id
        #createpackoperation
        pick_neg.move_line_ids[0].write({'result_package_id':package1.id,'qty_done':120})
        new_pack1=self.env['stock.move.line'].create({
            'product_id':product_neg.id,
            'product_uom_id':self.ref('uom.product_uom_unit'),
            'picking_id':pick_neg.id,
            'lot_id':lot_a.id,
            'qty_done':120,
            'result_package_id':package2.id,
            'location_id':self.ref('stock.stock_location_suppliers'),
            'location_dest_id':self.ref('stock.stock_location_stock')
        })
        new_pack2=self.env['stock.move.line'].create({
            'product_id':product_neg.id,
            'product_uom_id':self.ref('uom.product_uom_unit'),
            'picking_id':pick_neg.id,
            'result_package_id':package3.id,
            'qty_done':60,
            'location_id':self.ref('stock.stock_location_suppliers'),
            'location_dest_id':self.ref('stock.stock_location_stock')
        })

        #Transferthereceipt
        pick_neg._action_done()

        #Makeadeliveryorderof300piecestothecustomer
        vals={
            'name':'outgoingpicking(negativeproduct)',
            'partner_id':res_partner_4.id,
            'picking_type_id':self.ref('stock.picking_type_out'),
            'location_id':self.ref('stock.stock_location_stock'),
            'location_dest_id':self.ref('stock.stock_location_customers'),
            'move_lines':[(0,0,{
                'name':'NEG',
                'product_id':product_neg.id,
                'product_uom':product_neg.uom_id.id,
                'product_uom_qty':300.00,
                'location_id':self.ref('stock.stock_location_stock'),
                'location_dest_id':self.ref('stock.stock_location_customers'),
            })],
        }
        delivery_order_neg=self.env['stock.picking'].create(vals)
        delivery_order_neg.onchange_picking_type()
        delivery_order_neg.move_lines.onchange_product_id()

        #Assignandconfirm
        delivery_order_neg.action_confirm()
        delivery_order_neg.action_assign()

        #Insteadofdoingthe300pieces,youdecidetotakepallet1(donotmention
        #productinoperationhere)and140piecesfromlotA/pallet2and10piecesfrompallet3

        forrecindelivery_order_neg.move_line_ids:
            ifrec.package_id.name=='Palneg1':
                rec.qty_done=rec.product_qty
                rec.result_package_id=False
            elifrec.package_id.name=='Palneg2'andrec.lot_id.name=='Lotneg':
                rec.write({
                  'qty_done':140,
                  'result_package_id':False,
                })
            elifrec.package_id.name=='Palneg3':
                rec.qty_done=10
                rec.result_package_id=False

        #Processthispicking
        delivery_order_neg._action_done()

        #Checkthequantsthatyouhave-20piecespallet2instock,andatotalquantity
        #of50instockfrompallet3(shouldbe20+30,asithasbeensplitbyreservation)
        records=self.env['stock.quant'].search([('product_id','=',product_neg.id),('quantity','!=','0')])
        pallet_3_stock_qty=0
        forrecinrecords:
            ifrec.package_id.name=='Palneg2'andrec.location_id.id==self.ref('stock.stock_location_stock'):
                self.assertTrue(rec.quantity==-20,"Shouldhave-20piecesinstockonpallet2.Got"+str(rec.quantity))
                self.assertTrue(rec.lot_id.name=='Lotneg',"ItshouldhavekeptitsLot")
            elifrec.package_id.name=='Palneg3'andrec.location_id.id==self.ref('stock.stock_location_stock'):
                pallet_3_stock_qty+=rec.quantity
            else:
                self.assertTrue(rec.location_id.id!=self.ref('stock.stock_location_stock'),"Unrecognizedquantinstock")
        self.assertEqual(pallet_3_stock_qty,50,"Shouldhave50piecesinstockonpallet3")

        #Createapickingforreconcilingthenegativequant
        vals={
            'name':'reconciling_delivery',
            'partner_id':res_partner_4.id,
            'picking_type_id':self.ref('stock.picking_type_in'),
            'location_id':self.ref('stock.stock_location_suppliers'),
            'location_dest_id':self.ref('stock.stock_location_stock'),
            'move_lines':[(0,0,{
                'name':'NEG',
                'product_id':product_neg.id,
                'product_uom':product_neg.uom_id.id,
                'product_uom_qty':20.0,
                'location_id':self.ref('stock.stock_location_suppliers'),
                'location_dest_id':self.ref('stock.stock_location_stock'),
            })],
        }
        delivery_reconcile=self.env['stock.picking'].create(vals)
        delivery_reconcile.onchange_picking_type()
        delivery_reconcile.move_lines.onchange_product_id()

        #Receive20productswithlotneginstockwithanewincomingshipmentthatshouldbeonpallet2
        delivery_reconcile.action_confirm()
        lot=self.env["stock.production.lot"].search([
            ('product_id','=',product_neg.id),
            ('name','=','Lotneg')],limit=1)
        pack=self.env["stock.quant.package"].search([('name','=','Palneg2')],limit=1)
        delivery_reconcile.move_line_ids[0].write({'lot_id':lot.id,'qty_done':20.0,'result_package_id':pack.id})
        delivery_reconcile._action_done()

        #Checkthenegativequantwasreconciled
        neg_quants=self.env['stock.quant'].search([
            ('product_id','=',product_neg.id),
            ('quantity','<',0),
            ('location_id.id','!=',self.ref('stock.stock_location_suppliers'))])
        self.assertTrue(len(neg_quants)==0,"Negativequantsshouldhavebeenreconciled")
