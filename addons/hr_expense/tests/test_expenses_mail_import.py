#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.hr_expense.tests.commonimportTestExpenseCommon
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestExpensesMailImport(TestExpenseCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.product_a.default_code='product_a'
        cls.product_b.default_code='product_b'

    deftest_import_expense_from_email(self):
        message_parsed={
            'message_id':"the-world-is-a-ghetto",
            'subject':'%s%s'%(self.product_a.default_code,self.product_a.standard_price),
            'email_from':self.expense_user_employee.email,
            'to':'catchall@yourcompany.com',
            'body':"Don'tyouknow,thatforme,andforyou",
            'attachments':[],
        }

        expense=self.env['hr.expense'].message_new(message_parsed)

        self.assertRecordValues(expense,[{
            'product_id':self.product_a.id,
            'total_amount':920.0,
            'employee_id':self.expense_employee.id,
        }])

    deftest_import_expense_from_email_no_product(self):
        message_parsed={
            'message_id':"the-world-is-a-ghetto",
            'subject':'noproductcode800',
            'email_from':self.expense_user_employee.email,
            'to':'catchall@yourcompany.com',
            'body':"Don'tyouknow,thatforme,andforyou",
            'attachments':[],
        }

        expense=self.env['hr.expense'].message_new(message_parsed)

        self.assertRecordValues(expense,[{
            'product_id':False,
            'total_amount':800.0,
            'employee_id':self.expense_employee.id,
        }])

    deftest_import_expense_from_mail_parsing_subjects(self):

        defassertParsedValues(subject,currencies,exp_description,exp_amount,exp_product):
            product,amount,currency_id,description=self.env['hr.expense']\
                .with_user(self.expense_user_employee)\
                ._parse_expense_subject(subject,currencies)

            self.assertEqual(product,exp_product)
            self.assertAlmostEqual(amount,exp_amount)
            self.assertEqual(description,exp_description)

        #WithoutMulticurrencyaccess
        assertParsedValues(
            "product_abar$1205.91electrowizard",
            self.company_data['currency'],
            "barelectrowizard",
            1205.91,
            self.product_a,
        )

        #subjecthavingothercurrencythencompanycurrency,itshouldignoreothercurrencythencompanycurrency
        assertParsedValues(
            "foobar%s1406.91royalgiant"%self.currency_data['currency'].symbol,
            self.company_data['currency'],
            "foobar%sroyalgiant"%self.currency_data['currency'].symbol,
            1406.91,
            self.env['product.product'],
        )

        #WithMulticurrencyaccess
        self.expense_user_employee.groups_id|=self.env.ref('base.group_multi_currency')

        assertParsedValues(
            "product_afoobar$2205.92elitebarbarians",
            self.company_data['currency'],
            "foobarelitebarbarians",
            2205.92,
            self.product_a,
        )

        #subjecthavingothercurrencythencompanycurrency,itshouldacceptothercurrencybecausemulticurrencyisactivated
        assertParsedValues(
            "product_a%s2510.90chhotabheem"%self.currency_data['currency'].symbol,
            self.company_data['currency']+self.currency_data['currency'],
            "chhotabheem",
            2510.90,
            self.product_a,
        )

        #subjectwithoutproductandcurrency,shouldtakecompanycurrencyanddefaultproduct
        assertParsedValues(
            "foobar109.96speargoblins",
            self.company_data['currency']+self.currency_data['currency'],
            "foobarspeargoblins",
            109.96,
            self.env['product.product'],
        )

        #subjectwithcurrencysymbolatend
        assertParsedValues(
            "product_afoobar2910.94$infernodragon",
            self.company_data['currency']+self.currency_data['currency'],
            "foobarinfernodragon",
            2910.94,
            self.product_a,
        )

        #subjectwithnoamountandproduct
        assertParsedValues(
            "foobarmegaknight",
            self.company_data['currency']+self.currency_data['currency'],
            "foobarmegaknight",
            0.0,
            self.env['product.product'],
        )

        #pricewithacomma
        assertParsedValues(
            "foobar291,56$megaknight",
            self.company_data['currency']+self.currency_data['currency'],
            "foobarmegaknight",
            291.56,
            self.env['product.product'],
        )

        #pricewithoutdecimals
        assertParsedValues(
            "foobar291$megaknight",
            self.company_data['currency']+self.currency_data['currency'],
            "foobarmegaknight",
            291.0,
            self.env['product.product'],
        )

        assertParsedValues(
            "product_afoobar291.5$megaknight",
            self.company_data['currency']+self.currency_data['currency'],
            "foobarmegaknight",
            291.5,
            self.product_a,
        )
