from.commonimportPurchaseTestCommon


classTestPurchaseOrderProcess(PurchaseTestCommon):

    deftest_00_cancel_purchase_order_flow(self):
        """Testcancelpurchaseorderwithgroupuser."""

        #Inordertotestthecancelflow,startitfromcancelingconfirmedpurchaseorder.
        purchase_order=self.env['purchase.order'].create({
            'partner_id':self.env['res.partner'].create({'name':'MyPartner'}).id,
            'state':'draft',
        })
        po_edit_with_user=purchase_order.with_user(self.res_users_purchase_user)

        #Confirmthepurchaseorder.
        po_edit_with_user.button_confirm()

        #Checkthe"Approved"status afterconfirmedRFQ.
        self.assertEqual(po_edit_with_user.state,'purchase','Purchase:POstateshouldbe"Purchase')

        #Firstcancelreceptionsrelatedtothisorderifordershipped.
        po_edit_with_user.picking_ids.action_cancel()

        #Abletocancelpurchaseorder.
        po_edit_with_user.button_cancel()

        #Checkthatorderiscancelled.
        self.assertEqual(po_edit_with_user.state,'cancel','Purchase:POstateshouldbe"Cancel')
