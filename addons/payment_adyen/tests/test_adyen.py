#-*-coding:utf-8-*-

fromlxmlimportobjectify

fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.addons.payment_adyen.controllers.mainimportAdyenController
fromwerkzeugimporturls
importflectra.tests


classAdyenCommon(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #someCC(alwaysuseexpirationdate06/2016,cvc737,cid7373(amex))
        cls.amex=(('370000000000002','7373'))
        cls.dinersclub=(('36006666333344','737'))
        cls.discover=(('6011601160116611','737'),('644564456445644','737'))
        cls.jcb=(('3530111333300000','737'))
        cls.mastercard=(('5555444433331111','737'),('5555555555554444','737'))
        cls.visa=(('4111111111111111','737'),('4444333322221111','737'))
        cls.mcdebit=(('5500000000000004','737'))
        cls.visadebit=(('4400000000000008','737'))
        cls.maestro=(('6731012345678906','737'))
        cls.laser=(('630495060000000000','737'))
        cls.hipercard=(('6062828888666688','737'))
        cls.dsmastercard=(('5212345678901234','737','user','password'))
        cls.dsvisa=(('4212345678901237','737','user','password'))
        cls.mistercash=(('6703444444444449',None,'user','password'))
        cls.adyen=cls.env.ref('payment.payment_acquirer_adyen')
        cls.adyen.write({
            'adyen_merchant_account':'dummy',
            'adyen_skin_code':'dummy',
            'adyen_skin_hmac_key':'dummy',
            'state':'test',
        })


@flectra.tests.tagged('post_install','-at_install','external','-standard')
classAdyenForm(AdyenCommon):

    deftest_10_adyen_form_render(self):
        #besurenottodostupidthings
        adyen=self.adyen
        self.assertEqual(adyen.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------

        base_url=self.env['ir.config_parameter'].get_param('web.base.url')
        form_values={
            'merchantAccount':'OpenERPCOM',
            'merchantReference':'test_ref0',
            'skinCode':'cbqYWvVL',
            'paymentAmount':'1',
            'currencyCode':'EUR',
            'resURL':urls.url_join(base_url,AdyenController._return_url),
        }

        #renderthebutton
        res=adyen.render(
            'test_ref0',0.01,self.currency_euro.id,
            partner_id=None,
            partner_values=self.buyer_values)

        #checkformresult
        tree=objectify.fromstring(res)
        self.assertEqual(tree.get('action'),'https://test.adyen.com/hpp/pay.shtml','adyen:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit','shipBeforeDate','sessionValidity','shopperLocale','merchantSig']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'adyen:wrongvalueforinput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )
