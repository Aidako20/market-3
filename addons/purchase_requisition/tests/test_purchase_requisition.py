#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.purchase_requisition.tests.commonimportTestPurchaseRequisitionCommon
fromflectra.testsimportForm


classTestPurchaseRequisition(TestPurchaseRequisitionCommon):

    deftest_00_purchase_requisition_users(self):
        self.assertTrue(self.user_purchase_requisition_manager,'ManagerShouldbecreated')
        self.assertTrue(self.user_purchase_requisition_user,'UserShouldbecreated')

    deftest_01_cancel_purchase_requisition(self):
        self.requisition1.with_user(self.user_purchase_requisition_user).action_cancel()
        #Checkrequisitionaftercancelled.
        self.assertEqual(self.requisition1.state,'cancel','Requisitionshouldbeincancelledstate.')
        #Iresetrequisitionas"New".
        self.requisition1.with_user(self.user_purchase_requisition_user).action_draft()
        #Iduplicaterequisition.
        self.requisition1.with_user(self.user_purchase_requisition_user).copy()


    deftest_02_purchase_requisition(self):
        price_product09=34
        price_product13=62
        quantity=26

        #Createapruchaserequisitionwithtypeblanketorderandtwoproduct
        line1=(0,0,{'product_id':self.product_09.id,'product_qty':quantity,'product_uom_id':self.product_uom_id.id,'price_unit':price_product09})
        line2=(0,0,{'product_id':self.product_13.id,'product_qty':quantity,'product_uom_id':self.product_uom_id.id,'price_unit':price_product13})

        requisition_type=self.env['purchase.requisition.type'].create({
            'name':'Blankettest',
            'quantity_copy':'none'
        })
        requisition_blanket=self.env['purchase.requisition'].create({
            'line_ids':[line1,line2],
            'type_id':requisition_type.id,
            'vendor_id':self.res_partner_1.id,
        })

        #confirmtherequisition
        requisition_blanket.action_in_progress()

        #Checkforbothproductthatthenewsupplierinfo(purchase.requisition.vendor_id)isaddedtothepuchasetab
        #andcheckthequantity
        seller_partner1=self.res_partner_1
        supplierinfo09=self.env['product.supplierinfo'].search([
            ('name','=',seller_partner1.id),
            ('product_id','=',self.product_09.id),
            ('purchase_requisition_id','=',requisition_blanket.id),
        ])
        self.assertEqual(supplierinfo09.name,seller_partner1,'Thesupplierinfoisnotthegoodone')
        self.assertEqual(supplierinfo09.price,price_product09,'Thesupplierinfoisnotthegoodone')

        supplierinfo13=self.env['product.supplierinfo'].search([
            ('name','=',seller_partner1.id),
            ('product_id','=',self.product_13.id),
            ('purchase_requisition_id','=',requisition_blanket.id),
        ])
        self.assertEqual(supplierinfo13.name,seller_partner1,'Thesupplierinfoisnotthegoodone')
        self.assertEqual(supplierinfo13.price,price_product13,'Thesupplierinfoisnotthegoodone')

        #PuttherequisitionindoneStatus
        requisition_blanket.action_in_progress()
        requisition_blanket.action_done()

        self.assertFalse(self.env['product.supplierinfo'].search([('id','=',supplierinfo09.id)]),'Thesupplierinfoshouldberemoved')
        self.assertFalse(self.env['product.supplierinfo'].search([('id','=',supplierinfo13.id)]),'Thesupplierinfoshouldberemoved')

    deftest_06_purchase_requisition(self):
        """Createablanquetorderforaproductandavendoralreadylinkedvia
        asupplierinfo"""
        product=self.env['product.product'].create({
            'name':'test6',
        })
        product2=self.env['product.product'].create({
            'name':'test6',
        })
        vendor=self.env['res.partner'].create({
            'name':'vendor6',
        })
        supplier_info=self.env['product.supplierinfo'].create({
            'product_id':product.id,
            'name':vendor.id,
        })

        #createaemptyblanquetorder
        requisition_type=self.env['purchase.requisition.type'].create({
            'name':'Blankettest',
            'quantity_copy':'none'
        })
        line1=(0,0,{
            'product_id':product2.id,
            'product_uom_id':product2.uom_po_id.id,
            'price_unit':41,
            'product_qty':10,
        })
        requisition_blanket=self.env['purchase.requisition'].create({
            'line_ids':[line1],
            'type_id':requisition_type.id,
            'vendor_id':vendor.id,
        })
        requisition_blanket.action_in_progress()
        self.env['purchase.requisition.line'].create({
            'product_id':product.id,
            'product_qty':14.0,
            'requisition_id':requisition_blanket.id,
            'price_unit':10,
        })
        new_si=self.env['product.supplierinfo'].search([
            ('product_id','=',product.id),
            ('name','=',vendor.id)
        ])-supplier_info
        self.assertEqual(new_si.purchase_requisition_id,requisition_blanket,'theblanketorderisnotlinkedtothesupplierinfo')

    deftest_07_purchase_requisition(self):
        """
            Checkthattheanalyticaccountandtheaccounttagdefinedinthepurchaserequisitionline
            isusedinthepurchaseorderlinewhencreatingaPO.
        """
        analytic_account=self.env['account.analytic.account'].create({'name':'test_analytic_account'})
        analytic_tag=self.env['account.analytic.tag'].create({'name':'test_analytic_tag'})
        self.assertEqual(len(self.requisition1.line_ids),1)
        self.requisition1.line_ids[0].write({
            'account_analytic_id':analytic_account,
            'analytic_tag_ids':analytic_tag,
        })
        #Createpurchaseorderfrompurchaserequisition
        po_form=Form(self.env['purchase.order'].with_context(default_requisition_id=self.requisition1.id))
        po_form.partner_id=self.res_partner_1
        po=po_form.save()
        self.assertEqual(po.order_line.account_analytic_id.id,analytic_account.id,'Theanalyticaccountdefinedinthepurchaserequisitionlinemustbethesameastheonefromthepurchaseorderline.')
        self.assertEqual(po.order_line.analytic_tag_ids.id,analytic_tag.id,'Theanalyticaccounttagdefinedinthepurchaserequisitionlinemustbethesameastheonefromthepurchaseorderline.')
