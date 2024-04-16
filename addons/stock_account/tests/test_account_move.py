#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.addons.stock_account.tests.test_stockvaluationimport_create_accounting_data
fromflectra.tests.commonimporttagged,Form
fromflectraimportfields


@tagged("post_install","-at_install")
classTestAccountMove(AccountTestInvoicingCommon):
    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        (
            cls.stock_input_account,
            cls.stock_output_account,
            cls.stock_valuation_account,
            cls.expense_account,
            cls.stock_journal,
        )=_create_accounting_data(cls.env)

        #`all_categ`shouldnotbealtered,sowecantestthe`post_init`hookof`stock_account`
        cls.all_categ=cls.env.ref('product.product_category_all')

        cls.auto_categ=cls.env['product.category'].create({
            'name':'child_category',
            'parent_id':cls.all_categ.id,
            "property_stock_account_input_categ_id":cls.stock_input_account.id,
            "property_stock_account_output_categ_id":cls.stock_output_account.id,
            "property_stock_valuation_account_id":cls.stock_valuation_account.id,
            "property_stock_journal":cls.stock_journal.id,
            "property_valuation":"real_time",
            "property_cost_method":"standard",
        })
        cls.product_A=cls.env["product.product"].create(
            {
                "name":"ProductA",
                "type":"product",
                "default_code":"prda",
                "categ_id":cls.auto_categ.id,
                "taxes_id":[(5,0,0)],
                "supplier_taxes_id":[(5,0,0)],
                "lst_price":100.0,
                "standard_price":10.0,
                "property_account_income_id":cls.company_data["default_account_revenue"].id,
                "property_account_expense_id":cls.company_data["default_account_expense"].id,
            }
        )

    deftest_standard_perpetual_01_mc_01(self):
        rate=self.currency_data["rates"].sorted()[0].rate

        move_form=Form(self.env["account.move"].with_context(default_move_type="out_invoice"))
        move_form.partner_id=self.partner_a
        move_form.currency_id=self.currency_data["currency"]
        withmove_form.invoice_line_ids.new()asline_form:
            line_form.product_id=self.product_A
            line_form.tax_ids.clear()
        invoice=move_form.save()

        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_total)
        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_residual)
        self.assertEqual(len(invoice.mapped("line_ids")),2)
        self.assertEqual(len(invoice.mapped("line_ids.currency_id")),1)

        invoice._post()

        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_total)
        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_residual)
        self.assertEqual(len(invoice.mapped("line_ids")),4)
        self.assertEqual(len(invoice.mapped("line_ids").filtered("is_anglo_saxon_line")),2)
        self.assertEqual(len(invoice.mapped("line_ids.currency_id")),2)

    deftest_fifo_perpetual_01_mc_01(self):
        self.product_A.categ_id.property_cost_method="fifo"
        rate=self.currency_data["rates"].sorted()[0].rate

        move_form=Form(self.env["account.move"].with_context(default_move_type="out_invoice"))
        move_form.partner_id=self.partner_a
        move_form.currency_id=self.currency_data["currency"]
        withmove_form.invoice_line_ids.new()asline_form:
            line_form.product_id=self.product_A
            line_form.tax_ids.clear()
        invoice=move_form.save()

        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_total)
        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_residual)
        self.assertEqual(len(invoice.mapped("line_ids")),2)
        self.assertEqual(len(invoice.mapped("line_ids.currency_id")),1)

        invoice._post()

        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_total)
        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_residual)
        self.assertEqual(len(invoice.mapped("line_ids")),4)
        self.assertEqual(len(invoice.mapped("line_ids").filtered("is_anglo_saxon_line")),2)
        self.assertEqual(len(invoice.mapped("line_ids.currency_id")),2)

    deftest_average_perpetual_01_mc_01(self):
        self.product_A.categ_id.property_cost_method="average"
        rate=self.currency_data["rates"].sorted()[0].rate

        move_form=Form(self.env["account.move"].with_context(default_move_type="out_invoice"))
        move_form.partner_id=self.partner_a
        move_form.currency_id=self.currency_data["currency"]
        withmove_form.invoice_line_ids.new()asline_form:
            line_form.product_id=self.product_A
            line_form.tax_ids.clear()
        invoice=move_form.save()

        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_total)
        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_residual)
        self.assertEqual(len(invoice.mapped("line_ids")),2)
        self.assertEqual(len(invoice.mapped("line_ids.currency_id")),1)

        invoice._post()

        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_total)
        self.assertAlmostEqual(self.product_A.lst_price*rate,invoice.amount_residual)
        self.assertEqual(len(invoice.mapped("line_ids")),4)
        self.assertEqual(len(invoice.mapped("line_ids").filtered("is_anglo_saxon_line")),2)
        self.assertEqual(len(invoice.mapped("line_ids.currency_id")),2)

    deftest_basic_bill(self):
        """
        Whenbillingastorableproductwithabasiccategory(manual
        valuation),theaccountusedshouldbetheexpensesone.Thistest
        checkstheflowwithtwocompanies:
        -Onethatexistedbeforetheinstallationof`stock_account`(totest
        thepost-installhook)
        -Onecreatedafterthemoduleinstallation
        """
        first_company=self.env['res.company'].browse(1)
        self.env.user.company_ids|=first_company
        basic_product=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'product',
            'categ_id':self.all_categ.id,
        })

        forcompanyin(self.env.company|first_company):
            bill_form=Form(self.env['account.move'].with_company(company.id).with_context(default_move_type='in_invoice'))
            bill_form.partner_id=self.partner_a
            bill_form.invoice_date=fields.Date.today()
            withbill_form.invoice_line_ids.new()asline:
                line.product_id=basic_product
                line.price_unit=100
            bill=bill_form.save()
            bill.action_post()

            product_accounts=basic_product.product_tmpl_id.with_company(company.id).get_product_accounts()
            self.assertEqual(bill.invoice_line_ids.account_id,product_accounts['expense'])
