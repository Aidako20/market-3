#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimportForm,tagged
fromflectra.exceptionsimportAccessError


@tagged('post_install','-at_install')
classTestPurchaseInvoice(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #Createausers
        group_purchase_user=cls.env.ref('purchase.group_purchase_user')
        group_employee=cls.env.ref('base.group_user')
        group_partner_manager=cls.env.ref('base.group_partner_manager')

        cls.purchase_user=cls.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name':'Purchaseuser',
            'login':'purchaseUser',
            'email':'pu@flectrahq.com',
            'groups_id':[(6,0,[group_purchase_user.id,group_employee.id,group_partner_manager.id])],
        })

        cls.vendor=cls.env['res.partner'].create({
            'name':'Supplier',
            'email':'supplier.serv@supercompany.com',
        })

        user_type_expense=cls.env.ref('account.data_account_type_expenses')
        cls.account_expense_product=cls.env['account.account'].create({
            'code':'EXPENSE_PROD111',
            'name':'Expense-TestAccount',
            'user_type_id':user_type_expense.id,
        })
        #Createcategory
        cls.product_category=cls.env['product.category'].create({
            'name':'ProductCategorywithExpenseaccount',
            'property_account_expense_categ_id':cls.account_expense_product.id
        })
        cls.product=cls.env['product.product'].create({
            'name':"Product",
            'standard_price':200.0,
            'list_price':180.0,
            'type':'service',
        })

    deftest_create_purchase_order(self):
        """Checkapurchaseusercancreateavendorbillfromapurchaseorderbutnotpostit"""
        purchase_order_form=Form(self.env['purchase.order'].with_user(self.purchase_user))
        purchase_order_form.partner_id=self.vendor
        withpurchase_order_form.order_line.new()asline:
            line.name=self.product.name
            line.product_id=self.product
            line.product_qty=4
            line.price_unit=5

        purchase_order=purchase_order_form.save()
        purchase_order.button_confirm()

        purchase_order.order_line.qty_received=4
        purchase_order.action_create_invoice()
        invoice=purchase_order.invoice_ids
        withself.assertRaises(AccessError):
            invoice.action_post()

    deftest_read_purchase_order(self):
        """Checkthatapurchaseusercanreadallpurchaseorderand'in'invoices"""
        purchase_user_2=self.purchase_user.copy({
            'name':'Purchaseuser2',
            'login':'purchaseUser2',
            'email':'pu2@flectrahq.com',
        })

        purchase_order_form=Form(self.env['purchase.order'].with_user(purchase_user_2))
        purchase_order_form.partner_id=self.vendor
        withpurchase_order_form.order_line.new()asline:
            line.name=self.product.name
            line.product_id=self.product
            line.product_qty=4
            line.price_unit=5

        purchase_order_user2=purchase_order_form.save()
        purchase_order_user2.button_confirm()

        purchase_order_user2.order_line.qty_received=4
        purchase_order_user2.action_create_invoice()
        vendor_bill_user2=purchase_order_user2.invoice_ids

        #openpurchase_order_user2andvendor_bill_user2with`self.purchase_user`
        purchase_order_user1=Form(purchase_order_user2.with_user(self.purchase_user))
        purchase_order_user1=purchase_order_user1.save()
        vendor_bill_user1=Form(vendor_bill_user2.with_user(self.purchase_user))
        vendor_bill_user1=vendor_bill_user1.save()

    deftest_read_purchase_order_2(self):
        """Checkthata2purchaseuserswithopenthevendorbillthesame
        wayevenwitha'owndocumentsonly'recordrule."""

        #edittheaccount.moverecordruleforpurchaseuserinordertoensure
        #ausercanonlyseehisowninvoices
        rule=self.env.ref('purchase.purchase_user_account_move_rule')
        rule.domain_force="['&',('move_type','in',('in_invoice','in_refund','in_receipt')),('invoice_user_id','=',user.id)]"

        #createapurchaseandmakeavendorbillfromitaspurchaseuser2
        purchase_user_2=self.purchase_user.copy({
            'name':'Purchaseuser2',
            'login':'purchaseUser2',
            'email':'pu2@flectrahq.com',
        })

        purchase_order_form=Form(self.env['purchase.order'].with_user(purchase_user_2))
        purchase_order_form.partner_id=self.vendor
        withpurchase_order_form.order_line.new()asline:
            line.name=self.product.name
            line.product_id=self.product
            line.product_qty=4
            line.price_unit=5

        purchase_order_user2=purchase_order_form.save()
        purchase_order_user2.button_confirm()

        purchase_order_user2.order_line.qty_received=4
        purchase_order_user2.action_create_invoice()
        vendor_bill_user2=purchase_order_user2.invoice_ids

        #checkuser1cannotreadtheinvoice
        withself.assertRaises(AccessError):
            Form(vendor_bill_user2.with_user(self.purchase_user))

        #Checkthatcalling'action_view_invoice'returnthesameactiondespitetherecordrule
        action_user_1=purchase_order_user2.with_user(self.purchase_user).action_view_invoice()
        purchase_order_user2.invalidate_cache()
        action_user_2=purchase_order_user2.with_user(purchase_user_2).action_view_invoice()
        self.assertEqual(action_user_1,action_user_2)

    deftest_double_validation(self):
        """Onlypurchasemanagerscanapproveapurchaseorderwhendouble
        validationisenabled"""
        group_purchase_manager=self.env.ref('purchase.group_purchase_manager')
        order=self.env['purchase.order'].create({
            "partner_id":self.vendor.id,
            "order_line":[
                (0,0,{
                    'product_id':self.product.id,
                    'name':f'{self.product.name}{1:05}',
                    'price_unit':79.80,
                    'product_qty':15.0,
                }),
            ]})
        company=order.sudo().company_id
        company.po_double_validation='two_step'
        company.po_double_validation_amount=0
        self.purchase_user.write({
            'company_ids':[(4,company.id)],
            'company_id':company.id,
            'groups_id':[(3,group_purchase_manager.id)],
        })
        order.with_user(self.purchase_user).button_confirm()
        self.assertEqual(order.state,'toapprove')
        order.with_user(self.purchase_user).button_approve()
        self.assertEqual(order.state,'toapprove')
        self.purchase_user.groups_id+=group_purchase_manager
        order.with_user(self.purchase_user).button_approve()
        self.assertEqual(order.state,'purchase')
