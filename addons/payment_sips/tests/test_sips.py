#-*-coding:utf-8-*-
fromflectra.testsimporttagged
fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon


@tagged('post_install','-at_install','-standard','external')
classSipsTest(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.sips=cls.env.ref('payment.payment_acquirer_sips')
        cls.sips.write({
            'state':'test',
            'sips_merchant_id':'dummy_mid',
            'sips_secret':'dummy_secret',
        })

    deftest_10_sips_form_render(self):
        self.assertEqual(self.sips.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------

        #renderthebutton
        tx=self.env['payment.transaction'].create({
            'acquirer_id':self.sips.id,
            'amount':100.0,
            'reference':'SO404',
            'currency_id':self.currency_euro.id,
        })
        self.sips.render('SO404',100.0,self.currency_euro.id,values=self.buyer_values).decode('utf-8')

    deftest_20_sips_form_management(self):
        self.assertEqual(self.sips.state,'test','testwithouttestenvironment')

        #typicaldatapostedbySipsafterclienthassuccessfullypaid
        sips_post_data={
            'Data':'captureDay=0|captureMode=AUTHOR_CAPTURE|currencyCode=840|'
                    'merchantId=002001000000001|orderChannel=INTERNET|'
                    'responseCode=00|transactionDateTime=2020-04-08T06:15:59+02:00|'
                    'transactionReference=SO100x1|keyVersion=1|'
                    'acquirerResponseCode=00|amount=31400|authorisationId=0020000006791167|'
                    'paymentMeanBrand=IDEAL|paymentMeanType=CREDIT_TRANSFER|'
                    'customerIpAddress=127.0.0.1|returnContext={"return_url":'
                    '"/payment/process","reference":'
                    '"SO100x1"}|holderAuthentRelegation=N|holderAuthentStatus=|'
                    'transactionOrigin=INTERNET|paymentPattern=ONE_SHOT|customerMobilePhone=null|'
                    'mandateAuthentMethod=null|mandateUsage=null|transactionActors=null|'
                    'mandateId=null|captureLimitDate=20200408|dccStatus=null|dccResponseCode=null|'
                    'dccAmount=null|dccCurrencyCode=null|dccExchangeRate=null|'
                    'dccExchangeRateValidity=null|dccProvider=null|'
                    'statementReference=SO100x1|panEntryMode=MANUAL|walletType=null|'
                    'holderAuthentMethod=NO_AUTHENT_METHOD',
            'Encode':'',
            'InterfaceVersion':'HP_2.4',
            'Seal':'f03f64da6f57c171904d12bf709b1d6d3385131ac914e97a7e1db075ed438f3e',
            'locale':'en'
        }

        tx=self.env['payment.transaction'].create({
            'amount':314.0,
            'acquirer_id':self.sips.id,
            'currency_id':self.currency_euro.id,
            'reference':'SO100x1',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})

        #validateit
        tx.form_feedback(sips_post_data,'sips')
        self.assertEqual(tx.state,'done','Sips:validationdidnotputtxintodonestate')
        self.assertEqual(tx.acquirer_reference,'SO100x1','Sips:validationdidnotupdatetxid')
        
        #sameprocessforanpaymentinerroronsips'send
        sips_post_data={
            'Data':'captureDay=0|captureMode=AUTHOR_CAPTURE|currencyCode=840|'
                    'merchantId=002001000000001|orderChannel=INTERNET|responseCode=12|'
                    'transactionDateTime=2020-04-08T06:24:08+02:00|transactionReference=SO100x2|'
                    'keyVersion=1|amount=31400|customerIpAddress=127.0.0.1|returnContext={"return_url":'
                    '"/payment/process","reference":'
                    '"SO100x2"}|paymentPattern=ONE_SHOT|customerMobilePhone=null|mandateAuthentMethod=null|'
                    'mandateUsage=null|transactionActors=null|mandateId=null|captureLimitDate=null|'
                    'dccStatus=null|dccResponseCode=null|dccAmount=null|dccCurrencyCode=null|'
                    'dccExchangeRate=null|dccExchangeRateValidity=null|dccProvider=null|'
                    'statementReference=SO100x2|panEntryMode=null|walletType=null|holderAuthentMethod=null',
            'InterfaceVersion':'HP_2.4',
            'Seal':'6e1995ea5432580860a04d8515b6eb1507996f97b3c5fa04fb6d9568121a16a2'
        }
        tx=self.env['payment.transaction'].create({
            'amount':314.0,
            'acquirer_id':self.sips.id,
            'currency_id':self.currency_euro.id,
            'reference':'SO100x2',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})
        tx.form_feedback(sips_post_data,'sips')
        #checkstate
        self.assertEqual(tx.state,'cancel','Sips:erroneousvalidationdidnotputtxintoerrorstate')

    deftest_30_sips_badly_formatted_date(self):
        self.assertEqual(self.sips.state,'test','testwithouttestenvironment')

        #typicaldatapostedbySipsafterclienthassuccessfullypaid
        bad_date='2020-04-08T06:15:59+56:00'
        sips_post_data={
            'Data':'captureDay=0|captureMode=AUTHOR_CAPTURE|currencyCode=840|'
                    'merchantId=002001000000001|orderChannel=INTERNET|'
                    'responseCode=00|transactionDateTime=%s|'
                    'transactionReference=SO100x1|keyVersion=1|'
                    'acquirerResponseCode=00|amount=31400|authorisationId=0020000006791167|'
                    'paymentMeanBrand=IDEAL|paymentMeanType=CREDIT_TRANSFER|'
                    'customerIpAddress=127.0.0.1|returnContext={"return_url":'
                    '"/payment/process","reference":'
                    '"SO100x1"}|holderAuthentRelegation=N|holderAuthentStatus=|'
                    'transactionOrigin=INTERNET|paymentPattern=ONE_SHOT|customerMobilePhone=null|'
                    'mandateAuthentMethod=null|mandateUsage=null|transactionActors=null|'
                    'mandateId=null|captureLimitDate=20200408|dccStatus=null|dccResponseCode=null|'
                    'dccAmount=null|dccCurrencyCode=null|dccExchangeRate=null|'
                    'dccExchangeRateValidity=null|dccProvider=null|'
                    'statementReference=SO100x1|panEntryMode=MANUAL|walletType=null|'
                    'holderAuthentMethod=NO_AUTHENT_METHOD'%(bad_date,),
            'Encode':'',
            'InterfaceVersion':'HP_2.4',
            'Seal':'f03f64da6f57c171904d12bf709b1d6d3385131ac914e97a7e1db075ed438f3e',
            'locale':'en'
        }

        tx=self.env['payment.transaction'].create({
            'amount':314.0,
            'acquirer_id':self.sips.id,
            'currency_id':self.currency_euro.id,
            'reference':'SO100x1',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})

        #validateit
        tx.form_feedback(sips_post_data,'sips')
        self.assertEqual(tx.state,'done','Sips:validationdidnotputtxintodonestatewhendateformatwasweird')
