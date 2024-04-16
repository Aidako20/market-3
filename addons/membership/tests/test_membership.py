#-*-coding:utf-8-*-

importdatetime
fromdateutil.relativedeltaimportrelativedelta
fromunittest.mockimportpatch

importtime
fromflectra.addons.membership.tests.commonimportTestMembershipCommon
fromflectra.testsimporttagged
fromflectraimportfields


@tagged('post_install','-at_install')
classTestMembership(TestMembershipCommon):

    deftest_none_membership(self):
        self.membership_1.write({
            'membership_date_from':datetime.date.today()+relativedelta(years=-2),
            'membership_date_to':datetime.date.today()+relativedelta(years=-1),
        })

        self.partner_1.create_membership_invoice(self.membership_1,75.0)
        self.assertEqual(
            self.partner_1.membership_state,'none',
            'membership:outdatednonpaidsubscriptionshouldkeepinnon-memberstate')

    deftest_old_membership(self):
        self.membership_1.write({
            'membership_date_from':datetime.date.today()+relativedelta(years=-2),
            'membership_date_to':datetime.date.today()+relativedelta(years=-1),
        })

        self.partner_1.create_membership_invoice(self.membership_1,75.0)
        self.assertEqual(
            self.partner_1.membership_state,'none',
            'membership:outdatednonpaidsubscriptionshouldkeepinnon-memberstate')

        #subscribestoamembership
        self.partner_1.create_membership_invoice(self.membership_1,75.0)

        #checksforinvoices
        invoice=self.env['account.move'].search([('partner_id','=',self.partner_1.id)],limit=1)
        self.assertEqual(
            invoice.state,'draft',
            'membership:newsubscriptionshouldcreateadraftinvoice')
        self.assertEqual(
            invoice.invoice_line_ids[0].product_id,self.membership_1,
            'membership:newsubscriptionshouldcreatealinewiththemembershipasproduct')
        self.assertEqual(
            invoice.invoice_line_ids[0].price_unit,75.0,
            'membership:newsubscriptionshouldcreatealinewiththegivenpriceinsteadofproductprice')

        self.assertEqual(
            self.partner_1.membership_state,'none',
            'membership:oldmembershipunpaidshouldbeinnon-memberstate')

        #theinvoiceisopen->customergoestoinvoicedstatus
        invoice.action_post()

        self.assertEqual(
            self.partner_1.membership_state,'none',
            'membership:afteropeningtheinvoiceforoldmembership,itshouldremaininnonpaidstatus')

        #paymentprocess
        payment=self.env['account.payment'].create({
            'destination_account_id':invoice.line_ids.account_id.filtered(lambdaaccount:account.internal_type=='receivable').id,
            'payment_method_id':self.env['account.payment.method'].search([],limit=1).id,
            'payment_type':'inbound',
            'partner_type':'customer',
            'partner_id':invoice.partner_id.id,
            'amount':500,
            'company_id':self.env.company.id,
            'currency_id':self.env.company.currency_id.id,
        })
        payment.action_post()
        inv1_receivable=invoice.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')
        pay_receivable=payment.move_id.line_ids.filtered(lambdal:l.account_id.internal_type=='receivable')

        (inv1_receivable+pay_receivable).reconcile()

        #theinvoiceispaid->customergoestopaidstatus
        self.assertEqual(
            self.partner_1.membership_state,'old',
            'membership:afterpayingtheinvoice,customershouldbeinoldstatus')

        #checksecondpartnerthenassociatethem
        self.assertEqual(
            self.partner_2.membership_state,'free',
            'membership:freemembercustomershouldbeinfreestate')
        self.partner_2.write({'free_member':False,'associate_member':self.partner_1.id})
        self.assertEqual(
            self.partner_2.membership_state,'old',
            'membership:associatedcustomershouldbeinoldstate')

    deftest_paid_membership(self):
        self.assertEqual(
            self.partner_1.membership_state,'none',
            'membership:defaultmembershipstatusofpartnersshouldbeNone')

        #subscribestoamembership
        invoice=self.partner_1.create_membership_invoice(self.membership_1,75.0)

        self.assertEqual(
            invoice.state,'draft',
            'membership:newsubscriptionshouldcreateadraftinvoice')
        self.assertEqual(
            invoice.invoice_line_ids[0].product_id,self.membership_1,
            'membership:newsubscriptionshouldcreatealinewiththemembershipasproduct')
        self.assertEqual(
            invoice.invoice_line_ids[0].price_unit,75.0,
            'membership:newsubscriptionshouldcreatealinewiththegivenpriceinsteadofproductprice')

        self.assertEqual(
            self.partner_1.membership_state,'waiting',
            'membership:newmembershipshouldbeinwaitingstate')

        #theinvoiceisopen->customergoestoinvoicedstatus
        invoice.action_post()
        self.assertEqual(
            self.partner_1.membership_state,'invoiced',
            'membership:afteropeningtheinvoice,customershouldbeininvoicedstatus')

        #theinvoiceispaid->customergoestopaidstatus
        payment=self.env['account.payment.register']\
            .with_context(active_model='account.move',active_ids=invoice.ids)\
            .create({
                'amount':86.25
            })\
            ._create_payments()

        self.assertEqual(
            self.partner_1.membership_state,'paid',
            'membership:afterpayingtheinvoice,customershouldbeinpaidstatus')

        #checksecondpartnerthenassociatethem
        self.assertEqual(
            self.partner_2.membership_state,'free',
            'membership:freemembercustomershouldbeinfreestate')
        self.partner_2.write({'free_member':False,'associate_member':self.partner_1.id})
        self.assertEqual(
            self.partner_2.membership_state,'paid',
            'membership:associatedcustomershouldbeinpaidstate')

    deftest_cancel_membership(self):
        self.assertEqual(
            self.partner_1.membership_state,'none',
            'membership:defaultmembershipstatusofpartnersshouldbeNone')

        #subscribestoamembership
        invoice=self.partner_1.create_membership_invoice(self.membership_1,75.0)

        defpatched_today(*args,**kwargs):
            returnfields.Date.to_date('2019-01-01')

        withpatch.object(fields.Date,'today',patched_today):
            invoice.button_cancel()

        self.partner_1._compute_membership_state()
        self.assertEqual(invoice.state,'cancel')
        self.assertEqual(self.partner_1.membership_state,'canceled')

    deftest_apply_payment_term(self):
        """
            Checkifthepaymenttermdefinedonthepartnerisappliedtotheinvoice
        """
        pay_term_15_days_after_today=self.env['account.payment.term'].create({
            'name':'15daysaftertoday',
            'line_ids':[
                (0,0,{
                    'value':'balance',
                    'days':15,
                    'option':'day_after_invoice_date',
                }),
            ],
        })
        self.partner_1.write({
            'property_payment_term_id':pay_term_15_days_after_today.id,
        })
        invoice=self.partner_1.create_membership_invoice(self.membership_1,100.0)
        self.assertEqual(invoice.invoice_payment_term_id,pay_term_15_days_after_today)
