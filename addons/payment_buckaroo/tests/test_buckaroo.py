#-*-coding:utf-8-*-

fromlxmlimportobjectify
fromwerkzeugimporturls

importflectra
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.addons.payment_buckaroo.controllers.mainimportBuckarooController
fromflectra.toolsimportmute_logger


@flectra.tests.tagged('post_install','-at_install','external','-standard')
classBuckarooCommon(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        #getthebuckarooaccount
        cls.buckaroo=cls.env.ref('payment.payment_acquirer_buckaroo')
        cls.buckaroo.write({
            'brq_websitekey':'dummy',
            'brq_secretkey':'dummy',
            'state':'test',
        })

@flectra.tests.tagged('post_install','-at_install','external','-standard')
classBuckarooForm(BuckarooCommon):

    deftest_10_Buckaroo_form_render(self):
        base_url=self.env['ir.config_parameter'].get_param('web.base.url')
        #besurenottodostupidthings
        self.assertEqual(self.buckaroo.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------

        form_values={
            'add_returndata':'/payment/process',
            'Brq_websitekey':self.buckaroo.brq_websitekey,
            'Brq_amount':'2240.0',
            'Brq_currency':'EUR',
            'Brq_invoicenumber':'SO004',
            'Brq_signature':'f09bb79451a7ddef3178462ea52b07e55d34e99e', #updateme
            'brq_test':'True',
            'Brq_return':urls.url_join(base_url,BuckarooController._return_url),
            'Brq_returncancel':urls.url_join(base_url,BuckarooController._cancel_url),
            'Brq_returnerror':urls.url_join(base_url,BuckarooController._exception_url),
            'Brq_returnreject':urls.url_join(base_url,BuckarooController._reject_url),
            'Brq_culture':'en-US',
        }

        #renderthebutton
        res=self.buckaroo.render(
            'SO004',2240.0,self.currency_euro.id,
            partner_id=None,
            values=self.buyer_values)
        #checkformresult
        tree=objectify.fromstring(res)
        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'paypal:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://testcheckout.buckaroo.nl/html/','Buckaroo:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit','data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'Buckaroo:wrongvalueforinput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )

        #----------------------------------------
        #Test2:buttonusingtx+validation
        #----------------------------------------

        #createanewdrafttx
        tx=self.env['payment.transaction'].create({
            'amount':2240.0,
            'acquirer_id':self.buckaroo.id,
            'currency_id':self.currency_euro.id,
            'reference':'SO004',
            'partner_id':self.buyer_id,
        })

        #renderthebutton
        res=self.buckaroo.render(
            'should_be_erased',2240.0,self.currency_euro,
            partner_id=None,
            values=self.buyer_values)

        #checkformresult
        tree=objectify.fromstring(res)
        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'paypal:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://testcheckout.buckaroo.nl/html/','Buckaroo:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit','data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'Buckaroo:wrongvalueforforminput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )

    @mute_logger('flectra.addons.payment_buckaroo.models.payment','ValidationError')
    deftest_20_buckaroo_form_management(self):
        #besurenottodostupidthing
        self.assertEqual(self.buckaroo.state,'test','testwithouttestenvironment')

        #typicaldatapostedbybuckarooafterclienthassuccessfullypaid
        buckaroo_post_data={
            'BRQ_RETURNDATA':u'',
            'BRQ_AMOUNT':u'2240.00',
            'BRQ_CURRENCY':u'EUR',
            'BRQ_CUSTOMER_NAME':u'JandeTester',
            'BRQ_INVOICENUMBER':u'SO004',
            'brq_payment':u'573311D081B04069BD6336001611DBD4',
            'BRQ_PAYMENT_METHOD':u'paypal',
            'BRQ_SERVICE_PAYPAL_PAYERCOUNTRY':u'NL',
            'BRQ_SERVICE_PAYPAL_PAYEREMAIL':u'fhe@flectrahq.com',
            'BRQ_SERVICE_PAYPAL_PAYERFIRSTNAME':u'Jan',
            'BRQ_SERVICE_PAYPAL_PAYERLASTNAME':u'Tester',
            'BRQ_SERVICE_PAYPAL_PAYERMIDDLENAME':u'de',
            'BRQ_SERVICE_PAYPAL_PAYERSTATUS':u'verified',
            'Brq_signature':u'9e75e51cbcb6fbc798b40d1787cc5b7c36557d56',
            'BRQ_STATUSCODE':u'190',
            'BRQ_STATUSCODE_DETAIL':u'S001',
            'BRQ_STATUSMESSAGE':u'Transactionsuccessfullyprocessed',
            'BRQ_TEST':u'true',
            'BRQ_TIMESTAMP':u'2014-05-0812:41:21',
            'BRQ_TRANSACTIONS':u'D6106678E1D54EEB8093F5B3AC42EA7B',
            'BRQ_WEBSITEKEY':u'5xTGyGyPyl',
        }

        #shouldraiseerroraboutunknowntx
        withself.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(buckaroo_post_data,'buckaroo')

        tx=self.env['payment.transaction'].create({
            'amount':2240.0,
            'acquirer_id':self.buckaroo.id,
            'currency_id':self.currency_euro.id,
            'reference':'SO004',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})

        #validateit
        tx.form_feedback(buckaroo_post_data,'buckaroo')
        #checkstate
        self.assertEqual(tx.state,'done','Buckaroo:validationdidnotputtxintodonestate')
        self.assertEqual(tx.acquirer_reference,buckaroo_post_data.get('BRQ_TRANSACTIONS'),'Buckaroo:validationdidnotupdatetxpayid')

        #resettx
        tx=self.env['payment.transaction'].create({
            'amount':2240.0,
            'acquirer_id':self.buckaroo.id,
            'currency_id':self.currency_euro.id,
            'reference':'SO004-2',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})

        buckaroo_post_data['BRQ_INVOICENUMBER']='SO004-2'
        #nowbuckaroopostisok:trytomodifytheSHASIGN
        buckaroo_post_data['Brq_signature']='54d928810e343acf5fb0c3ee75fd747ff159ef7a'
        withself.assertRaises(ValidationError):
            tx.form_feedback(buckaroo_post_data,'buckaroo')
        #simulateanerror
        buckaroo_post_data['BRQ_STATUSCODE']='2'
        buckaroo_post_data['Brq_signature']='9138e2bf09a708a4eb485ce7777e5406898b689d'
        tx.form_feedback(buckaroo_post_data,'buckaroo')

        #checkstate
        self.assertEqual(tx.state,'cancel','Buckaroo:erroneousvalidationdidnotputtxintoerrorstate')
