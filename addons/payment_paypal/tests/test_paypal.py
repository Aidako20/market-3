#-*-coding:utf-8-*-

fromflectraimportfields
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.addons.payment_paypal.controllers.mainimportPaypalController
fromwerkzeugimporturls

fromflectra.toolsimportmute_logger
fromflectra.testsimporttagged

fromlxmlimportobjectify


classPaypalCommon(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.paypal=cls.env.ref('payment.payment_acquirer_paypal')
        cls.paypal.write({
            'paypal_email_account':'dummy',
            'state':'test',
        })

        #someCC
        cls.amex=(('378282246310005','123'),('371449635398431','123'))
        cls.amex_corporate=(('378734493671000','123'))
        cls.autralian_bankcard=(('5610591081018250','123'))
        cls.dinersclub=(('30569309025904','123'),('38520000023237','123'))
        cls.discover=(('6011111111111117','123'),('6011000990139424','123'))
        cls.jcb=(('3530111333300000','123'),('3566002020360505','123'))
        cls.mastercard=(('5555555555554444','123'),('5105105105105100','123'))
        cls.visa=(('4111111111111111','123'),('4012888888881881','123'),('4222222222222','123'))
        cls.dankord_pbs=(('76009244561','123'),('5019717010103742','123'))
        cls.switch_polo=(('6331101999990016','123'))


@tagged('post_install','-at_install','external','-standard')
classPaypalForm(PaypalCommon):

    deftest_10_paypal_form_render(self):
        base_url=self.env['ir.config_parameter'].get_param('web.base.url')
        #besurenottodostupidthings
        self.paypal.write({'paypal_email_account':'tde+paypal-facilitator@flectrahq.com','fees_active':False})
        self.assertEqual(self.paypal.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------

        #renderthebutton
        res=self.paypal.render(
            'test_ref0',0.01,self.currency_euro.id,
            values=self.buyer_values)

        form_values={
            'cmd':'_xclick',
            'business':'tde+paypal-facilitator@flectrahq.com',
            'item_name':'%s:test_ref0'%(self.paypal.company_id.name),
            'item_number':'test_ref0',
            'first_name':'Norbert',
            'last_name':'Buyer',
            'amount':'0.01',
            'bn':'FlectraInc_SP',
            'currency_code':'EUR',
            'address1':'HugeStreet2/543',
            'city':'SinCity',
            'zip':'1000',
            'rm':'2',
            'country':'BE',
            'email':'norbert.buyer@example.com',
            'return':urls.url_join(base_url,PaypalController._return_url),
            'notify_url':urls.url_join(base_url,PaypalController._notify_url),
            'cancel_return':urls.url_join(base_url,PaypalController._cancel_url),
            'custom':'{"return_url":"/payment/process"}',
        }

        #checkformresult
        tree=objectify.fromstring(res)

        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'paypal:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://www.sandbox.paypal.com/cgi-bin/webscr','paypal:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit','data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'paypal:wrongvalueforinput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )

    deftest_11_paypal_form_with_fees(self):
        #besurenottodostupidthings
        self.assertEqual(self.paypal.state,'test','testwithouttestenvironment')

        #updateacquirer:computefees
        self.paypal.write({
            'fees_active':True,
            'fees_dom_fixed':1.0,
            'fees_dom_var':0.35,
            'fees_int_fixed':1.5,
            'fees_int_var':0.50,
        })

        #renderthebutton
        res=self.paypal.render(
            'test_ref0',12.50,self.currency_euro.id,
            values=self.buyer_values)

        #checkformresult
        handling_found=False
        tree=objectify.fromstring(res)

        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'paypal:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://www.sandbox.paypal.com/cgi-bin/webscr','paypal:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['handling']:
                handling_found=True
                self.assertEqual(form_input.get('value'),'1.57','paypal:wrongcomputedfees')
        self.assertTrue(handling_found,'paypal:fees_activedidnotaddhandlinginputinrenderedform')

    @mute_logger('flectra.addons.payment_paypal.models.payment','ValidationError')
    deftest_20_paypal_form_management(self):
        #besurenottodostupidthings
        self.assertEqual(self.paypal.state,'test','testwithouttestenvironment')

        #typicaldatapostedbypaypalafterclienthassuccessfullypaid
        paypal_post_data={
            'protection_eligibility':u'Ineligible',
            'last_name':u'Poilu',
            'txn_id':u'08D73520KX778924N',
            'receiver_email':'dummy',
            'payment_status':u'Pending',
            'payment_gross':u'',
            'tax':u'0.00',
            'residence_country':u'FR',
            'address_state':u'Alsace',
            'payer_status':u'verified',
            'txn_type':u'web_accept',
            'address_street':u'Av.delaPelouse,87648672Mayet',
            'handling_amount':u'0.00',
            'payment_date':u'03:21:19Nov18,2013PST',
            'first_name':u'Norbert',
            'item_name':u'test_ref_2',
            'address_country':u'France',
            'charset':u'windows-1252',
            'custom':u'{"return_url":"/payment/process"}',
            'notify_version':u'3.7',
            'address_name':u'NorbertPoilu',
            'pending_reason':u'multi_currency',
            'item_number':u'test_ref_2',
            'receiver_id':u'dummy',
            'transaction_subject':u'',
            'business':u'dummy',
            'test_ipn':u'1',
            'payer_id':u'VTDKRZQSAHYPS',
            'verify_sign':u'An5ns1Kso7MWUdW4ErQKJJJ4qi4-AVoiUf-3478q3vrSmqh08IouiYpM',
            'address_zip':u'75002',
            'address_country_code':u'FR',
            'address_city':u'Paris',
            'address_status':u'unconfirmed',
            'mc_currency':u'EUR',
            'shipping':u'0.00',
            'payer_email':u'tde+buyer@flectrahq.com',
            'payment_type':u'instant',
            'mc_gross':u'1.95',
            'ipn_track_id':u'866df2ccd444b',
            'quantity':u'1'
        }

        #shouldraiseerroraboutunknowntx
        withself.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(paypal_post_data,'paypal')

        #createtx
        tx=self.env['payment.transaction'].create({
            'amount':1.95,
            'acquirer_id':self.paypal.id,
            'currency_id':self.currency_euro.id,
            'reference':'test_ref_2',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})

        #validateit
        tx.form_feedback(paypal_post_data,'paypal')
        #check
        self.assertEqual(tx.state,'pending','paypal:wrongstateafterreceivingavalidpendingnotification')
        self.assertEqual(tx.state_message,'multi_currency','paypal:wrongstatemessageafterreceivingavalidpendingnotification')
        self.assertEqual(tx.acquirer_reference,'08D73520KX778924N','paypal:wrongtxn_idafterreceivingavalidpendingnotification')

        #updatetx
        tx.write({
            'state':'draft',
            'acquirer_reference':False})

        #updatenotificationfrompaypal
        paypal_post_data['payment_status']='Completed'
        #validateit
        tx.form_feedback(paypal_post_data,'paypal')
        #check
        self.assertEqual(tx.state,'done','paypal:wrongstateafterreceivingavalidpendingnotification')
        self.assertEqual(tx.acquirer_reference,'08D73520KX778924N','paypal:wrongtxn_idafterreceivingavalidpendingnotification')
        self.assertEqual(fields.Datetime.to_string(tx.date),'2013-11-1811:21:19','paypal:wrongvalidationdate')

    deftest_21_paypal_compute_fees(self):
        #Ifthemerchantneedstokeep100€,thetransactionwillbeequalto103.30€.
        #Inthisway,Paypalwilltake103.30*2.9%+0.30=3.30€
        #Andthemerchantwilltake103.30-3.30=100€
        self.paypal.write({
            'fees_active':True,
            'fees_int_fixed':0.30,
            'fees_int_var':2.90,
        })
        total_fee=self.paypal.paypal_compute_fees(100,False,False)
        self.assertEqual(round(total_fee,2),3.3,'WrongcomputationofthePaypalfees')
