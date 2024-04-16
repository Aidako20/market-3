#-*-coding:utf-8-*-
importflectra
fromflectraimportfields
fromflectra.exceptionsimportValidationError
fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromunittest.mockimportpatch
from.importstripe_mocks
from..models.paymentimportSTRIPE_SIGNATURE_AGE_TOLERANCE
fromflectra.toolsimportmute_logger


classStripeCommon(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.stripe=cls.env.ref('payment.payment_acquirer_stripe')
        cls.stripe.write({
            'stripe_secret_key':'sk_test_KJtHgNwt2KS3xM7QJPr4O5E8',
            'stripe_publishable_key':'pk_test_QSPnimmb4ZhtkEy3Uhdm4S6J',
            'stripe_webhook_secret':'whsec_vG1fL6CMUouQ7cObF2VJprLVXT5jBLxB',
            'state':'test',
        })
        cls.token=cls.env['payment.token'].create({
            'name':'TestCard',
            'acquirer_id':cls.stripe.id,
            'acquirer_ref':'cus_G27S7FqQ2w3fuH',
            'stripe_payment_method':'pm_1FW3DdAlCFm536g8eQoSCejY',
            'partner_id':cls.buyer.id,
            'verified':True,
        })
        cls.ideal_icon=cls.env.ref("payment.payment_icon_cc_ideal")
        cls.bancontact_icon=cls.env.ref("payment.payment_icon_cc_bancontact")
        cls.p24_icon=cls.env.ref("payment.payment_icon_cc_p24")
        cls.eps_icon=cls.env.ref("payment.payment_icon_cc_eps")
        cls.giropay_icon=cls.env.ref("payment.payment_icon_cc_giropay")
        cls.all_icons=[cls.ideal_icon,cls.bancontact_icon,cls.p24_icon,cls.eps_icon,cls.giropay_icon]
        cls.stripe.write({'payment_icon_ids':[(5,0,0)]})


@flectra.tests.tagged('post_install','-at_install','-standard','external')
classStripeTest(StripeCommon):

    defrun(self,result=None):
        withmute_logger('flectra.addons.payment.models.payment_acquirer','flectra.addons.payment_stripe.models.payment'):
            StripeCommon.run(self,result)

    deftest_10_stripe_s2s(self):
        self.assertEqual(self.stripe.state,'test','testwithouttestenvironment')
        #Createtransaction
        tx=self.env['payment.transaction'].create({
            'reference':'stripe_test_10_%s'%fields.datetime.now().strftime('%Y%m%d_%H%M%S'),
            'currency_id':self.currency_euro.id,
            'acquirer_id':self.stripe.id,
            'partner_id':self.buyer_id,
            'payment_token_id':self.token.id,
            'type':'server2server',
            'amount':115.0
        })
        tx.with_context(off_session=True).stripe_s2s_do_transaction()

        #Checkstate
        self.assertEqual(tx.state,'done','Stripe:Transcationhasbeendiscarded.')

    deftest_20_stripe_form_render(self):
        self.assertEqual(self.stripe.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------

        #renderthebutton
        self.stripe.render('SO404',320.0,self.currency_euro.id,values=self.buyer_values).decode('utf-8')

    deftest_30_stripe_form_management(self):
        self.assertEqual(self.stripe.state,'test','testwithouttestenvironment')
        ref='stripe_test_30_%s'%fields.datetime.now().strftime('%Y%m%d_%H%M%S')
        tx=self.env['payment.transaction'].create({
            'amount':4700.0,
            'acquirer_id':self.stripe.id,
            'currency_id':self.currency_euro.id,
            'reference':ref,
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id,
            'payment_token_id':self.token.id,
        })
        res=tx.with_context(off_session=True)._stripe_create_payment_intent()
        tx.stripe_payment_intent=res.get('payment_intent')

        #typicaldatapostedbyStripeafterclienthassuccessfullypaid
        stripe_post_data={'reference':ref}
        #validateit
        tx.form_feedback(stripe_post_data,'stripe')
        self.assertEqual(tx.state,'done','Stripe:validationdidnotputtxintodonestate')
        self.assertEqual(tx.acquirer_reference,stripe_post_data.get('id'),'Stripe:validationdidnotupdatetxid')

    deftest_add_available_payment_method_types_local_enabled(self):
        self.stripe.payment_icon_ids=[(6,0,[i.idforiinself.all_icons])]
        tx_values={
            'billing_partner_country':self.env.ref('base.be'),
            'currency':self.env.ref('base.EUR'),
            'type':'form'
        }
        stripe_session_data={}

        self.stripe._add_available_payment_method_types(stripe_session_data,tx_values)

        actual={pmtforkey,pmtinstripe_session_data.items()ifkey.startswith('payment_method_types')}
        self.assertEqual({'card','bancontact'},actual)

    deftest_add_available_payment_method_types_local_enabled_2(self):
        self.stripe.payment_icon_ids=[(6,0,[i.idforiinself.all_icons])]
        tx_values={
            'billing_partner_country':self.env.ref('base.pl'),
            'currency':self.env.ref('base.PLN'),
            'type':'form'
        }
        stripe_session_data={}

        self.stripe._add_available_payment_method_types(stripe_session_data,tx_values)

        actual={pmtforkey,pmtinstripe_session_data.items()ifkey.startswith('payment_method_types')}
        self.assertEqual({'card','p24'},actual)

    deftest_add_available_payment_method_types_pmt_does_not_exist(self):
        self.bancontact_icon.unlink()
        tx_values={
            'billing_partner_country':self.env.ref('base.be'),
            'currency':self.env.ref('base.EUR'),
            'type':'form'
        }
        stripe_session_data={}

        self.stripe._add_available_payment_method_types(stripe_session_data,tx_values)

        actual={pmtforkey,pmtinstripe_session_data.items()ifkey.startswith('payment_method_types')}
        self.assertEqual({'card','bancontact'},actual)

    deftest_add_available_payment_method_types_local_disabled(self):
        tx_values={
            'billing_partner_country':self.env.ref('base.be'),
            'currency':self.env.ref('base.EUR'),
            'type':'form'
        }
        stripe_session_data={}

        self.stripe._add_available_payment_method_types(stripe_session_data,tx_values)

        actual={pmtforkey,pmtinstripe_session_data.items()ifkey.startswith('payment_method_types')}
        self.assertEqual({'card'},actual)

    deftest_add_available_payment_method_types_local_all_but_bancontact(self):
        self.stripe.payment_icon_ids=[(4,icon.id)foriconinself.all_iconsificon.name.lower()!='bancontact']
        tx_values={
            'billing_partner_country':self.env.ref('base.be'),
            'currency':self.env.ref('base.EUR'),
            'type':'form'
        }
        stripe_session_data={}

        self.stripe._add_available_payment_method_types(stripe_session_data,tx_values)

        actual={pmtforkey,pmtinstripe_session_data.items()ifkey.startswith('payment_method_types')}
        self.assertEqual({'card'},actual)

    deftest_add_available_payment_method_types_recurrent(self):
        tx_values={
            'billing_partner_country':self.env.ref('base.be'),
            'currency':self.env.ref('base.EUR'),
            'type':'form_save'
        }
        stripe_session_data={}

        self.stripe._add_available_payment_method_types(stripe_session_data,tx_values)

        actual={pmtforkey,pmtinstripe_session_data.items()ifkey.startswith('payment_method_types')}
        self.assertEqual({'card'},actual)

    deftest_discarded_webhook(self):
        self.assertFalse(self.env['payment.acquirer']._handle_stripe_webhook(dict(type='payment.intent.succeeded')))

    deftest_handle_checkout_webhook_no_secret(self):
        self.stripe.stripe_webhook_secret=None

        withself.assertRaises(ValidationError):
            self.env['payment.acquirer']._handle_stripe_webhook(dict(type='checkout.session.completed'))

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_handle_checkout_webhook(self,dt,request):
        #passsignatureverification
        dt.utcnow.return_value.timestamp.return_value=1591264652
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body
        #testsetup
        tx=self.env['payment.transaction'].create({
            'reference':'tx_ref_test_handle_checkout_webhook',
            'currency_id':self.currency_euro.id,
            'acquirer_id':self.stripe.id,
            'partner_id':self.buyer_id,
            'payment_token_id':self.token.id,
            'type':'server2server',
            'amount':30
        })
        res=tx.with_context(off_session=True)._stripe_create_payment_intent()
        tx.stripe_payment_intent=res.get('payment_intent')
        stripe_object=stripe_mocks.checkout_session_object

        actual=self.stripe._handle_checkout_webhook(stripe_object)

        self.assertTrue(actual)

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_handle_checkout_webhook_wrong_amount(self,dt,request):
        #passsignatureverification
        dt.utcnow.return_value.timestamp.return_value=1591264652
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body
        #testsetup
        bad_tx=self.env['payment.transaction'].create({
            'reference':'tx_ref_test_handle_checkout_webhook_wrong_amount',
            'currency_id':self.currency_euro.id,
            'acquirer_id':self.stripe.id,
            'partner_id':self.buyer_id,
            'payment_token_id':self.token.id,
            'type':'server2server',
            'amount':10
        })
        wrong_amount_stripe_payment_intent=bad_tx.with_context(off_session=True)._stripe_create_payment_intent()
        tx=self.env['payment.transaction'].create({
            'reference':'tx_ref_test_handle_checkout_webhook',
            'currency_id':self.currency_euro.id,
            'acquirer_id':self.stripe.id,
            'partner_id':self.buyer_id,
            'payment_token_id':self.token.id,
            'type':'server2server',
            'amount':30
        })
        tx.stripe_payment_intent=wrong_amount_stripe_payment_intent.get('payment_intent')
        stripe_object=stripe_mocks.checkout_session_object

        actual=self.env['payment.acquirer']._handle_checkout_webhook(stripe_object)

        self.assertFalse(actual)

    deftest_handle_checkout_webhook_no_flectra_tx(self):
        stripe_object=stripe_mocks.checkout_session_object

        actual=self.stripe._handle_checkout_webhook(stripe_object)

        self.assertFalse(actual)

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_handle_checkout_webhook_no_stripe_tx(self,dt,request):
        #passsignatureverification
        dt.utcnow.return_value.timestamp.return_value=1591264652
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body
        #testsetup
        self.env['payment.transaction'].create({
            'reference':'tx_ref_test_handle_checkout_webhook',
            'currency_id':self.currency_euro.id,
            'acquirer_id':self.stripe.id,
            'partner_id':self.buyer_id,
            'payment_token_id':self.token.id,
            'type':'server2server',
            'amount':30
        })
        stripe_object=stripe_mocks.checkout_session_object

        withself.assertRaises(ValidationError):
            self.stripe._handle_checkout_webhook(stripe_object)

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_verify_stripe_signature(self,dt,request):
        dt.utcnow.return_value.timestamp.return_value=1591264652
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body

        actual=self.stripe._verify_stripe_signature()

        self.assertTrue(actual)

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_verify_stripe_signature_tampered_body(self,dt,request):
        dt.utcnow.return_value.timestamp.return_value=1591264652
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body.replace(b'1500',b'10')

        withself.assertRaises(ValidationError):
            self.stripe._verify_stripe_signature()

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_verify_stripe_signature_wrong_secret(self,dt,request):
        dt.utcnow.return_value.timestamp.return_value=1591264652
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body
        self.stripe.write({
            'stripe_webhook_secret':'whsec_vG1fL6CMUouQ7cObF2VJprL_TAMPERED',
        })

        withself.assertRaises(ValidationError):
            self.stripe._verify_stripe_signature()

    @patch('flectra.addons.payment_stripe.models.payment.request')
    @patch('flectra.addons.payment_stripe.models.payment.datetime')
    deftest_verify_stripe_signature_too_old(self,dt,request):
        dt.utcnow.return_value.timestamp.return_value=1591264652+STRIPE_SIGNATURE_AGE_TOLERANCE+1
        request.httprequest.headers={'Stripe-Signature':stripe_mocks.checkout_session_signature}
        request.httprequest.data=stripe_mocks.checkout_session_body

        withself.assertRaises(ValidationError):
            self.stripe._verify_stripe_signature()
