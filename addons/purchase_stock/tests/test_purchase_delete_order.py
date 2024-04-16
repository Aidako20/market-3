#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError
from.commonimportPurchaseTestCommon


classTestDeleteOrder(PurchaseTestCommon):

    deftest_00_delete_order(self):
        '''Testcasefordeletingpurchaseorderwithpurchaseusergroup'''

        #Inordertotestdeleteprocessonpurchaseorder,triedtodeleteaconfirmedorderandcheckErrorMessage.
        partner=self.env['res.partner'].create({'name':'MyPartner'})

        purchase_order=self.env['purchase.order'].create({
            'partner_id':partner.id,
            'state':'purchase',
        })
        purchase_order_1=purchase_order.with_user(self.res_users_purchase_user)
        withself.assertRaises(UserError):
            purchase_order_1.unlink()

        #Delete'cancelled'purchaseorderwithusergroup
        purchase_order=self.env['purchase.order'].create({
            'partner_id':partner.id,
            'state':'purchase',
        })
        purchase_order_2=purchase_order.with_user(self.res_users_purchase_user)
        purchase_order_2.button_cancel()
        self.assertEqual(purchase_order_2.state,'cancel','POiscancelled!')
        purchase_order_2.unlink()

        #Delete'draft'purchaseorderwithusergroup
        purchase_order=self.env['purchase.order'].create({
            'partner_id':partner.id,
            'state':'draft',
        })
        purchase_order_3=purchase_order.with_user(self.res_users_purchase_user)
        purchase_order_3.button_cancel()
        self.assertEqual(purchase_order_3.state,'cancel','POiscancelled!')
        purchase_order_3.unlink()
