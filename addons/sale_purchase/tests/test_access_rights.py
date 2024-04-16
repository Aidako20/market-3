#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportAccessError
fromflectra.addons.sale_purchase.tests.commonimportTestCommonSalePurchaseNoChart
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestAccessRights(TestCommonSalePurchaseNoChart):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #Createausers
        group_sale_user=cls.env.ref('sales_team.group_sale_salesman')
        group_purchase_user=cls.env.ref('purchase.group_purchase_user')
        cls.user_salesperson=cls.env['res.users'].with_context(no_reset_password=True).create({
            'name':'LeGrandJojoUser',
            'login':'grand.jojo',
            'email':'grand.jojo@chansonbelge.com',
            'groups_id':[(6,0,[group_sale_user.id])]
        })
        cls.user_purchaseperson=cls.env['res.users'].with_context(no_reset_password=True).create({
            'name':'Jean-LucFonck',
            'login':'jl.fonck',
            'email':'jl.fonck@chansonbelge.com',
            'groups_id':[(6,0,[group_purchase_user.id])]
        })

    deftest_access_saleperson(self):
        """Checkasaleperson(only)cangenerateaPOandaPOusercannotconfirmaSO"""
        SaleOrder=self.env['sale.order'].with_context(tracking_disable=True)

        sale_order=SaleOrder.with_user(self.user_salesperson).create({
            'partner_id':self.partner_a.id,
            'user_id':self.user_salesperson.id
        })

        sol_service_purchase=self.env['sale.order.line'].with_user(self.user_salesperson).create({
            'name':self.service_purchase_1.name,
            'product_id':self.service_purchase_1.id,
            'product_uom_qty':4,
            'product_uom':self.service_purchase_1.uom_id.id,
            'price_unit':self.service_purchase_1.list_price,
            'order_id':sale_order.id,
            'tax_id':False,
        })

        #confirmingSOwillcreatethePOevenifyoudon'thavetherights
        sale_order.action_confirm()
        sale_order.action_cancel()

        self.assertTrue(sale_order.name,"SalepersoncanreaditsownSO")

        action=sale_order.sudo().action_view_purchase_orders()

        #trytoaccessPOassaleperson
        withself.assertRaises(AccessError):
            purchase_orders=self.env['purchase.order'].with_user(self.user_salesperson).browse(action['res_id'])
            purchase_orders.read()

        #trytoaccessPOaspurchaseperson
        purchase_orders=self.env['purchase.order'].with_user(self.user_purchaseperson).browse(action['res_id'])
        purchase_orders.read()

        #trytoaccessthePOlinesfromtheSO,assaleperson
        withself.assertRaises(AccessError):
            sol_service_purchase.with_user(self.user_salesperson).purchase_line_ids.read()
