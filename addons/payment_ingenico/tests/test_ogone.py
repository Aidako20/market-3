#-*-coding:utf-8-*-

fromlxmlimportobjectify
importtime

fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.addons.payment_ingenico.controllers.mainimportOgoneController
fromwerkzeugimporturls

fromflectra.toolsimportmute_logger
fromflectra.testsimporttagged


@tagged('post_install','-at_install','external','-standard')
classOgonePayment(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.ogone=cls.env.ref('payment.payment_acquirer_ogone')
        cls.ogone.write({
            'ogone_pspid':'dummy',
            'ogone_userid':'dummy',
            'ogone_password':'dummy',
            'ogone_shakey_in':'dummy',
            'ogone_shakey_out':'dummy',
            'state':'test',
        })

    deftest_10_ogone_form_render(self):
        base_url=self.env['ir.config_parameter'].get_param('web.base.url')
        #besurenottodostupidthing
        self.assertEqual(self.ogone.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering+shasign
        #----------------------------------------

        form_values={
            'PSPID':'dummy',
            'ORDERID':'test_ref0',
            'AMOUNT':'1',
            'CURRENCY':'EUR',
            'LANGUAGE':'en_US',
            'CN':'NorbertBuyer',
            'EMAIL':'norbert.buyer@example.com',
            'OWNERZIP':'1000',
            'OWNERADDRESS':'HugeStreet2/543',
            'OWNERCTY':'Belgium',
            'OWNERTOWN':'SinCity',
            'OWNERTELNO':'003212345678',
            'SHASIGN':'815f67b8ff70d234ffcf437c13a9fa7f807044cc',
            'ACCEPTURL':urls.url_join(base_url,OgoneController._accept_url),
            'DECLINEURL':urls.url_join(base_url,OgoneController._decline_url),
            'EXCEPTIONURL':urls.url_join(base_url,OgoneController._exception_url),
            'CANCELURL':urls.url_join(base_url,OgoneController._cancel_url),
        }

        #renderthebutton
        res=self.ogone.render(
            'test_ref0',0.01,self.currency_euro.id,
            partner_id=None,
            partner_values=self.buyer_values)

        #checkformresult
        tree=objectify.fromstring(res)
        self.assertEqual(tree.get('action'),'https://secure.ogone.com/ncol/test/orderstandard.asp','ogone:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'ogone:wrongvalueforinput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )

        #----------------------------------------
        #Test2:buttonusingtx+validation
        #----------------------------------------

        #createanewdrafttx
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.ogone.id,
            'currency_id':self.currency_euro.id,
            'reference':'test_ref0',
            'partner_id':self.buyer_id})
        #renderthebutton
        res=self.ogone.render(
            'should_be_erased',0.01,self.currency_euro,
            tx_id=tx.id,
            partner_id=None,
            partner_values=self.buyer_values)

        #checkformresult
        tree=objectify.fromstring(res)
        self.assertEqual(tree.get('action'),'https://secure.ogone.com/ncol/test/orderstandard.asp','ogone:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'ingenico:wrongvalueforforminput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')])
            )

    @mute_logger('flectra.addons.payment_ingenico.models.payment','ValidationError')
    deftest_20_ogone_form_management(self):
        #besurenottodostupidthing
        self.assertEqual(self.ogone.state,'test','testwithouttestenvironment')

        #typicaldatapostedbyogoneafterclienthassuccessfullypaid
        ogone_post_data={
            'orderID':u'test_ref_2',
            'STATUS':u'9',
            'CARDNO':u'XXXXXXXXXXXX0002',
            'PAYID':u'25381582',
            'CN':u'NorbertBuyer',
            'NCERROR':u'0',
            'TRXDATE':u'11/15/13',
            'IP':u'85.201.233.72',
            'BRAND':u'VISA',
            'ACCEPTANCE':u'test123',
            'currency':u'EUR',
            'amount':u'1.95',
            'SHASIGN':u'7B7B0ED9CBC4A85543A9073374589033A62A05A5',
            'ED':u'0315',
            'PM':u'CreditCard'
        }

        #shouldraiseerroraboutunknowntx
        withself.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(ogone_post_data)

        #createtx
        tx=self.env['payment.transaction'].create({
            'amount':1.95,
            'acquirer_id':self.ogone.id,
            'currency_id':self.currency_euro.id,
            'reference':'test_ref_2-1',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})
        #validateit
        tx.form_feedback(ogone_post_data)
        #checkstate
        self.assertEqual(tx.state,'done','ogone:validationdidnotputtxintodonestate')
        self.assertEqual(tx.ogone_payid,ogone_post_data.get('PAYID'),'ogone:validationdidnotupdatetxpayid')

        #resettx
        tx=self.env['payment.transaction'].create({
            'amount':1.95,
            'acquirer_id':self.ogone.id,
            'currency_id':self.currency_euro.id,
            'reference':'test_ref_2-2',
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id})

        #nowogonepostisok:trytomodifytheSHASIGN
        ogone_post_data['SHASIGN']='a4c16bae286317b82edb49188d3399249a784691'
        withself.assertRaises(ValidationError):
            tx.form_feedback(ogone_post_data)

        #simulateanerror
        ogone_post_data['STATUS']=2
        ogone_post_data['SHASIGN']='a4c16bae286317b82edb49188d3399249a784691'
        tx.form_feedback(ogone_post_data)
        #checkstate
        self.assertEqual(tx.state,'cancel','ogone:erroneousvalidationdidnotputtxintoerrorstate')

    deftest_30_ogone_s2s(self):
        test_ref='test_ref_%.15f'%time.time()
        #besurenottodostupidthing
        self.assertEqual(self.ogone.state,'test','testwithouttestenvironment')

        #createanewdrafttx
        tx=self.env['payment.transaction'].create({
            'amount':0.01,
            'acquirer_id':self.ogone.id,
            'currency_id':self.currency_euro.id,
            'reference':test_ref,
            'partner_id':self.buyer_id,
            'type':'server2server',
        })

        #createanalias
        res=tx.ogone_s2s_create_alias({
            'expiry_date_mm':'01',
            'expiry_date_yy':'2015',
            'holder_name':'NorbertPoilu',
            'number':'4000000000000002',
            'brand':'VISA'})

        res=tx.ogone_s2s_execute({})
