#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromlxmlimportobjectify
fromwerkzeugimporturls

fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


classPayUlatamCommon(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.payulatam=cls.env.ref('payment.payment_acquirer_payulatam')
        cls.payulatam.write({
            'payulatam_account_id':'dummy',
            'payulatam_merchant_id':'dummy',
            'payulatam_api_key':'dummy',
            'state':'test',
        })


@tagged('post_install','-at_install','external','-standard')
classPayUlatamForm(PayUlatamCommon):

    @classmethod
    defsetUpClass(cls):
        super(PayUlatamForm,cls).setUpClass()

        #typicaldatapostedbypayulatamafterclienthassuccessfullypaid
        cls.payulatam_post_confirmation_approved_data={
            'currency':'EUR',
            'reference_sale':'TestTransaction',
            'response_message_pol':'APPROVED',
            'sign':'df4ce433330a1400df065948d3e5795e',
            'state_pol':'4',
            'transaction_id':'7008bc34-8258-4857-b866-7d4d7982bd73',
            'value':'0.01',
            'merchant_id':'dummy',
        }

    deftest_10_payulatam_form_render(self):
        base_url=self.env['ir.config_parameter'].get_param('web.base.url')
        self.assertEqual(self.payulatam.state,'test','testwithouttestenvironment')
        self.payulatam.write({
            'payulatam_merchant_id':'dummy',
            'payulatam_account_id':'dummy',
            'payulatam_api_key':'dummy',
        })

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------
        self.env['payment.transaction'].create({
            'reference':'test_ref0',
            'amount':0.001,
            'currency_id':self.currency_euro.id,
            'acquirer_id':self.payulatam.id,
            'partner_id':self.buyer_id
        })

        #renderthebutton
        res=self.payulatam.render(
            'test_ref0',0.01,self.currency_euro.id,
            values=self.buyer_values)

        form_values={
            'merchantId':'dummy',
            'accountId':'dummy',
            'description':'test_ref0',
            'referenceCode':'test',
            'amount':'0.01',
            'currency':'EUR',
            'tax':'0',
            'taxReturnBase':'0',
            'buyerEmail':'norbert.buyer@example.com',
            'responseUrl':urls.url_join(base_url,'/payment/payulatam/response'),
            'confirmationUrl':urls.url_join(base_url,'/payment/payulatam/webhook'),
            'extra1':None
        }
        #checkformresult
        tree=objectify.fromstring(res)

        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'payulatam:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu/','payulatam:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit','data_set','signature','referenceCode']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'payulatam:wrongvalueforinput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )

    deftest_20_payulatam_form_management(self):
        self.assertEqual(self.payulatam.state,'test','testwithouttestenvironment')

        #typicaldatapostedbypayulatamafterclienthassuccessfullypaid
        payulatam_post_data={
            'installmentsNumber':'1',
            'lapPaymentMethod':'VISA',
            'description':'test_ref0',
            'currency':'EUR',
            'extra2':'',
            'lng':'es',
            'transactionState':'7',
            'polPaymentMethod':'211',
            'pseCycle':'',
            'pseBank':'',
            'referenceCode':'test_ref_10',
            'reference_pol':'844164756',
            'signature':'31af67235afba03be244224fe4d71da8',
            'pseReference3':'',
            'buyerEmail':'admin@yourcompany.example.com',
            'lapResponseCode':'PENDING_TRANSACTION_CONFIRMATION',
            'pseReference2':'',
            'cus':'',
            'orderLanguage':'es',
            'TX_VALUE':'0.01',
            'risk':'',
            'trazabilityCode':'',
            'extra3':'',
            'pseReference1':'',
            'polTransactionState':'14',
            'polResponseCode':'25',
            'merchant_name':'TestPayUTestcomercio',
            'merchant_url':'http://pruebaslapv.xtrweb.com',
            'extra1':'/shop/payment/validate',
            'message':'PENDING',
            'lapPaymentMethodType':'CARD',
            'polPaymentMethodType':'7',
            'telephone':'7512354',
            'merchantId':'dummy',
            'transactionId':'b232989a-4aa8-42d1-bace-153236eee791',
            'authorizationCode':'',
            'lapTransactionState':'PENDING',
            'TX_TAX':'.00',
            'merchant_address':'Av123Calle12'
        }

        #createtx
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.payulatam.id,
            'currency_id':self.currency_euro.id,
            'reference':'test_ref_10',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id,
            'partner_id':self.buyer_id})

        #validatetransaction
        tx.form_feedback(payulatam_post_data,'payulatam')
        #check
        self.assertEqual(tx.state,'pending','Payulatam:wrongstateafterreceivingavalidpendingnotification')
        self.assertEqual(tx.state_message,'PENDING','Payulatam:wrongstatemessageafterreceivingavalidpendingnotification')
        self.assertEqual(tx.acquirer_reference,'b232989a-4aa8-42d1-bace-153236eee791','PayULatam:wrongtxn_idafterreceivingavalidpendingnotification')

        #updatetransaction
        tx.write({
            'state':'draft',
            'acquirer_reference':False})

        #updatenotificationfrompayulatam
        payulatam_post_data['lapTransactionState']='APPROVED'
        #validatetransaction
        tx.form_feedback(payulatam_post_data,'payulatam')
        #checktransaction
        self.assertEqual(tx.state,'done','payulatam:wrongstateafterreceivingavalidpendingnotification')
        self.assertEqual(tx.acquirer_reference,'b232989a-4aa8-42d1-bace-153236eee791','payulatam:wrongtxn_idafterreceivingavalidpendingnotification')

    @mute_logger('flectra.addons.payment_payulatam.controllers.main')
    deftest_confirmation_webhook_approved(self):
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.payulatam.id,
            'currency_id':self.currency_euro.id,
            'reference':'TestTransaction',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id,
            'partner_id':self.buyer_id})
        self.assertEqual(tx.state,'draft')

        res=self.url_open('/payment/payulatam/webhook',
                            data=self.payulatam_post_confirmation_approved_data)
        tx.invalidate_cache()
        self.assertEqual(res.status_code,200,'ShouldbeOK')
        self.assertEqual(res.text,'',"Bodyshouldbeempty")
        self.assertEqual(tx.state,'done')

    @mute_logger('flectra.addons.payment_payulatam.controllers.main')
    deftest_confirmation_webhook_approved_bad_signature(self):
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.payulatam.id,
            'currency_id':self.currency_euro.id,
            'reference':'TestTransaction',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id,
            'partner_id':self.buyer_id})
        self.assertEqual(tx.state,'draft')

        post_data=self.payulatam_post_confirmation_approved_data
        post_data['sign']="wrongsignature"

        res=self.url_open('/payment/payulatam/webhook',data=post_data)
        tx.invalidate_cache()
        self.assertEqual(res.status_code,200,'ShouldbeOK')
        self.assertEqual(tx.state,'draft')

    @mute_logger('flectra.addons.payment_payulatam.controllers.main')
    deftest_confirmation_webhook_declined(self):
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.payulatam.id,
            'currency_id':self.currency_euro.id,
            'reference':'TestTransaction',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id,
            'partner_id':self.buyer_id})
        self.assertEqual(tx.state,'draft')

        post_data=self.payulatam_post_confirmation_approved_data
        post_data['state_pol']='6'
        post_data['response_message_pol']='DECLINED'
        post_data['sign']='d2f074547e8b79d3ddb333e10f0de8b7'
        res=self.url_open('/payment/payulatam/webhook',data=post_data)
        tx.invalidate_cache()
        self.assertEqual(res.status_code,200,'ShouldbeOK')
        self.assertEqual(res.text,'',"Bodyshouldbeempty")
        self.assertEqual(tx.state,'cancel')

    @mute_logger('flectra.addons.payment_payulatam.controllers.main')
    deftest_confirmation_webhook_expired(self):
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.payulatam.id,
            'currency_id':self.currency_euro.id,
            'reference':'TestTransaction',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id,
            'partner_id':self.buyer_id})
        self.assertEqual(tx.state,'draft')

        post_data=self.payulatam_post_confirmation_approved_data
        post_data['state_pol']='5'
        post_data['response_message_pol']='EXPIRED'
        post_data['sign']='f8eb1d10496b87af9706fedf97200619'
        res=self.url_open('/payment/payulatam/webhook',data=post_data)
        tx.invalidate_cache()
        self.assertEqual(res.status_code,200,'ShouldbeOK')
        self.assertEqual(res.text,'',"Bodyshouldbeempty")
        self.assertEqual(tx.state,'cancel')
