#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectraimportfields


@tagged('post_install','-at_install')
classTestAccountInvoiceReport(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.invoices=cls.env['account.move'].create([
            {
                'move_type':'out_invoice',
                'partner_id':cls.partner_a.id,
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'currency_id':cls.currency_data['currency'].id,
                'invoice_line_ids':[
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':3,
                        'price_unit':750,
                    }),
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':1,
                        'price_unit':3000,
                    }),
                ]
            },
            {
                'move_type':'out_receipt',
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'currency_id':cls.currency_data['currency'].id,
                'invoice_line_ids':[
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':1,
                        'price_unit':6000,
                    }),
                ]
            },
            {
                'move_type':'out_refund',
                'partner_id':cls.partner_a.id,
                'invoice_date':fields.Date.from_string('2017-01-01'),
                'currency_id':cls.currency_data['currency'].id,
                'invoice_line_ids':[
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':1,
                        'price_unit':1200,
                    }),
                ]
            },
            {
                'move_type':'in_invoice',
                'partner_id':cls.partner_a.id,
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'currency_id':cls.currency_data['currency'].id,
                'invoice_line_ids':[
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':1,
                        'price_unit':60,
                    }),
                ]
            },
            {
                'move_type':'in_receipt',
                'partner_id':cls.partner_a.id,
                'invoice_date':fields.Date.from_string('2016-01-01'),
                'currency_id':cls.currency_data['currency'].id,
                'invoice_line_ids':[
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':1,
                        'price_unit':60,
                    }),
                ]
            },
            {
                'move_type':'in_refund',
                'partner_id':cls.partner_a.id,
                'invoice_date':fields.Date.from_string('2017-01-01'),
                'currency_id':cls.currency_data['currency'].id,
                'invoice_line_ids':[
                    (0,None,{
                        'product_id':cls.product_a.id,
                        'quantity':1,
                        'price_unit':12,
                    }),
                ]
            },
        ])

    defassertInvoiceReportValues(self,expected_values_list):
        reports=self.env['account.invoice.report'].search([('company_id','=',self.company_data['company'].id)],order='price_subtotalDESC,quantityASC')
        expected_values_dict=[{
            'price_average':vals[0],
            'price_subtotal':vals[1],
            'quantity':vals[2],
        }forvalsinexpected_values_list]

        self.assertRecordValues(reports,expected_values_dict)

    deftest_invoice_report_multiple_types(self):
        self.assertInvoiceReportValues([
            #price_average  price_subtotal quantity
            [2000,          2000,          1],
            [1000,          1000,          1],
            [250,           750,           3],
            [6,             6,             1],
            [20,            -20,          -1],
            [20,            -20,          -1],
            [600,           -600,         -1],
        ])
