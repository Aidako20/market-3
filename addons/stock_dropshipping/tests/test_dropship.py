#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon,Form
fromflectra.toolsimportmute_logger


classTestDropship(common.TransactionCase):
    deftest_change_qty(self):
        #enablethedropshipandMTOrouteontheproduct
        prod=self.env['product.product'].create({'name':'LargeDesk'})
        dropshipping_route=self.env.ref('stock_dropshipping.route_drop_shipping')
        mto_route=self.env.ref('stock.route_warehouse0_mto')
        prod.write({'route_ids':[(6,0,[dropshipping_route.id,mto_route.id])]})

        #addavendor
        vendor1=self.env['res.partner'].create({'name':'vendor1'})
        seller1=self.env['product.supplierinfo'].create({
            'name':vendor1.id,
            'price':8,
        })
        prod.write({'seller_ids':[(6,0,[seller1.id])]})

        #selloneunitofthisproduct
        cust=self.env['res.partner'].create({'name':'customer1'})
        so=self.env['sale.order'].create({
            'partner_id':cust.id,
            'partner_invoice_id':cust.id,
            'partner_shipping_id':cust.id,
            'order_line':[(0,0,{
                'name':prod.name,
                'product_id':prod.id,
                'product_uom_qty':1.00,
                'product_uom':prod.uom_id.id,
                'price_unit':12,
            })],
            'pricelist_id':self.env.ref('product.list0').id,
            'picking_policy':'direct',
        })
        so.action_confirm()
        po=self.env['purchase.order'].search([('group_id','=',so.procurement_group_id.id)])
        po_line=po.order_line

        #ChecktheqtyontheP0
        self.assertAlmostEqual(po_line.product_qty,1.00)

        #UpdateqtyonSOandcheckPO
        so.write({'order_line':[[1,so.order_line.id,{'product_uom_qty':2.00}]]})
        self.assertAlmostEqual(po_line.product_qty,2.00)

        #Createanewsoline
        sol2=self.env['sale.order.line'].create({
            'order_id':so.id,
            'name':prod.name,
            'product_id':prod.id,
            'product_uom_qty':3.00,
            'product_uom':prod.uom_id.id,
            'price_unit':12,
        })
        #thereisanewline
        pol2=po.order_line-po_line
        #thefirstlineisunchanged
        self.assertAlmostEqual(po_line.product_qty,2.00)
        #thenewlinematchesthenewlineontheso
        self.assertAlmostEqual(pol2.product_qty,sol2.product_uom_qty)

    deftest_00_dropship(self):

        #Createavendor
        supplier_dropship=self.env['res.partner'].create({'name':'VendorofDropshippingtest'})

        #Createnewproductwithoutanyroutes
        drop_shop_product=self.env['product.product'].create({
            'name':"Pendrive",
            'type':"product",
            'categ_id':self.env.ref('product.product_category_1').id,
            'lst_price':100.0,
            'standard_price':0.0,
            'uom_id':self.env.ref('uom.product_uom_unit').id,
            'uom_po_id':self.env.ref('uom.product_uom_unit').id,
            'seller_ids':[(0,0,{
                'delay':1,
                'name':supplier_dropship.id,
                'min_qty':2.0
            })]
        })

        #Createasalesorderwithalineof200PCEincomingshipment,withroute_iddropshipping
        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'MyTestPartner'})
        so_form.payment_term_id=self.env.ref('account.account_payment_term_end_following_month')
        withmute_logger('flectra.tests.common.onchange'):
            #otherwisecomplainsthatthere'snotenoughinventoryand
            #apparentlythat'snormalaccordingto@jcoand@sle
            withso_form.order_line.new()asline:
                line.product_id=drop_shop_product
                line.product_uom_qty=200
                line.price_unit=1.00
                line.route_id=self.env.ref('stock_dropshipping.route_drop_shipping')
        sale_order_drp_shpng=so_form.save()

        #Confirmsalesorder
        sale_order_drp_shpng.action_confirm()

        #Checkthesalesordercreatedaprocurementgroupwhichhasaprocurementof200pieces
        self.assertTrue(sale_order_drp_shpng.procurement_group_id,'SOshouldhaveprocurementgroup')

        #Checkaquotationwascreatedtoacertainvendorandconfirmsoitbecomesaconfirmedpurchaseorder
        purchase=self.env['purchase.order'].search([('partner_id','=',supplier_dropship.id)])
        self.assertTrue(purchase,"anRFQshouldhavebeencreatedbythescheduler")
        purchase.button_confirm()
        self.assertEqual(purchase.state,'purchase','Purchaseordershouldbeintheapprovedstate')
        self.assertEqual(len(purchase.ids),1,'Thereshouldbeonepicking')

        #Sendthe200pieces
        purchase.picking_ids.move_lines.quantity_done=purchase.picking_ids.move_lines.product_qty
        purchase.picking_ids.button_validate()

        #CheckonemovelinewascreatedinCustomerslocationwith200pieces
        move_line=self.env['stock.move.line'].search([
            ('location_dest_id','=',self.env.ref('stock.stock_location_customers').id),
            ('product_id','=',drop_shop_product.id)])
        self.assertEqual(len(move_line.ids),1,'Thereshouldbeexactlyonemoveline')
