#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeugimporturls
fromlxmlimportobjectify

importflectra

fromflectra.toolsimportmute_logger
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment.tests.commonimportPaymentAcquirerCommon
fromflectra.addons.payment_alipay.controllers.mainimportAlipayController

@flectra.tests.tagged('post_install','-at_install','external','-standard')
classAlipayTest(PaymentAcquirerCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.currency_yuan=cls.env['res.currency'].search([('name','=','CNY'),
                                                              '|',
                                                              ('active','=',True),
                                                              ('active','=',False)],limit=1)
        cls.alipay=cls.env.ref('payment.payment_acquirer_alipay')
        cls.alipay.write({
            'alipay_merchant_partner_id':'dummy',
            'alipay_md5_signature_key':'dummy',
            'alipay_seller_email':'dummy',
            'state':'test',
        })

    deftest_10_alipay_form_render(self):
        base_url=self.env['ir.config_parameter'].get_param('web.base.url')
        self.assertEqual(self.alipay.state,'test','testwithouttestenvironment')

        #----------------------------------------
        #Test:buttondirectrendering
        #----------------------------------------

        #renderthebutton
        res=self.alipay.render(
            'test_ref0',0.01,self.currency_euro.id,
            values=self.buyer_values)

        form_values={
            '_input_charset':'utf-8',
            'notify_url':urls.url_join(base_url,AlipayController._notify_url),
            'out_trade_no':'SO12345-1',
            'partner':self.alipay.alipay_merchant_partner_id,
            'return_url':urls.url_join(base_url,AlipayController._return_url),
            'subject':'test_ref0',
            'total_fee':'0.01',
        }

        ifself.alipay.alipay_payment_method=='standard_checkout':
            form_values.update({
                'service':'create_forex_trade',
                'currency':'EUR',
                'product_code':'NEW_OVERSEAS_SELLER',
            })
        else:
            form_values.update({
                'payment_type':'1',
                'seller_email':self.alipay.alipay_seller_email,
                'service':'create_direct_pay_by_user'
            })
        sign=self.alipay._build_sign(form_values)

        form_values.update({'sign':sign,'sign_type':'MD5'})
        #checkformresult
        tree=objectify.fromstring(res)

        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'Alipay:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://openapi.alipaydev.com/gateway.do','alipay:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['submit','data_set','sign','out_trade_no']:
                continue
            self.assertEqual(form_input.get('value'),form_values[form_input.get('name')],'alipay:wrongvalueforinput%s:received%sinsteadof%s'%(form_input.get('name'),form_input.get('value'),form_values[form_input.get('name')]))

    deftest_11_alipay_form_with_fees(self):
        self.assertEqual(self.alipay.state,'test','testwithouttestenvironment')

        #updateacquirer:computefees
        self.alipay.write({
            'fees_active':True,
            'fees_dom_fixed':1.0,
            'fees_dom_var':0.35,
            'fees_int_fixed':1.5,
            'fees_int_var':0.50,
        })

        #renderthebutton
        res=self.alipay.render(
            'test_ref0',12.50,self.currency_euro.id,
            values=self.buyer_values)

        tree=objectify.fromstring(res)

        data_set=tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set),1,'alipay:Found%d"data_set"inputinsteadof1'%len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'),'https://openapi.alipaydev.com/gateway.do','alipay:wrongformPOSTurl')
        forform_inputintree.input:
            ifform_input.get('name')in['total_fee']:
                self.assertEqual(form_input.get('value'),'14.07','alipay:wrongcomputedfees') #totalamount=amount+fees

    @mute_logger('flectra.addons.payment_alipay.models.payment','ValidationError')
    deftest_20_alipay_form_management(self):
        self.alipay.alipay_payment_method='standard_checkout'
        self._test_20_alipay_form_management()
        self.alipay.alipay_payment_method='express_checkout'
        self._test_20_alipay_form_management()

    def_test_20_alipay_form_management(self):
        self.assertEqual(self.alipay.state,'test','testwithouttestenvironment')

        #typicaldatapostedbyalipayafterclienthassuccessfullypaid
        alipay_post_data={
            'trade_no':'2017112321001003690200384552',
            'reference':'test_ref_'+self.alipay.alipay_payment_method,
            'total_fee':1.95,
            'trade_status':'TRADE_CLOSED',
        }

        ifself.alipay.alipay_payment_method=='express_checkout':
            alipay_post_data.update({
                'seller_email':self.alipay.alipay_seller_email,
            })
        else:
            alipay_post_data.update({
                'currency':'EUR',
            })

        alipay_post_data['sign']=self.alipay._build_sign(alipay_post_data)
        #shouldraiseerroraboutunknowntx
        withself.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(alipay_post_data,'alipay')

        ifself.alipay.alipay_payment_method=='express_checkout':
            currency=self.currency_yuan
        else:
            currency=self.currency_euro

        #createtx
        tx=self.env['payment.transaction'].create({
            'amount':1.95,
            'acquirer_id':self.alipay.id,
            'currency_id':currency.id,
            'reference':'test_ref_'+self.alipay.alipay_payment_method,
            'partner_name':'NorbertBuyer',
            'partner_country_id':self.country_france.id
        })

        #validatetx
        tx.form_feedback(alipay_post_data,'alipay')
        #checktx
        self.assertEqual(tx.state,'cancel','alipay:wrongstateafterreceivingavalidpendingnotification')
        self.assertEqual(tx.acquirer_reference,'2017112321001003690200384552','alipay:wrongtxn_idafterreceivingavalidpendingnotification')

        #updatetx
        tx.write({'state':'draft','acquirer_reference':False})

        #updatenotificationfromalipayshouldnotgothroughsinceithasalreadybeensetas'done'
        ifself.alipay.alipay_payment_method=='standard_checkout':
            alipay_post_data['trade_status']='TRADE_FINISHED'
        else:
            alipay_post_data['trade_status']='TRADE_SUCCESS'
        alipay_post_data['sign']=self.alipay._build_sign(alipay_post_data)
        #validatetx
        tx.form_feedback(alipay_post_data,'alipay')
        #checktx
        self.assertEqual(tx.acquirer_reference,'2017112321001003690200384552','alipay:notificationshouldnotgothroughtsinceithasalreadybeenvalidated')

        #thistimeitshouldgothroughsincethetransactionisnotvalidatedyet
        tx.write({'state':'draft','acquirer_reference':False})
        tx.form_feedback(alipay_post_data,'alipay')
        self.assertEqual(tx.state,'done','alipay:wrongstateafterreceivingavalidpendingnotification')
        self.assertEqual(tx.acquirer_reference,'2017112321001003690200384552','alipay:wrongtxn_idafterreceivingavalidpendingnotification')

    @mute_logger('flectra.addons.payment_alipay.models.payment','ValidationError')
    deftest_30_alipay_bad_configuration(self):
        self.alipay.alipay_payment_method='express_checkout'

        #shouldraiseerrorsince`express_checkout`mustonlybeusedwithCNYcurrency
        withself.assertRaises(ValidationError):
            #createtx
            tx=self.env['payment.transaction'].create({
                'acquirer_id':self.alipay.id,
                'amount':4,
                'currency_id':self.currency_euro.id,
                'reference':'test_ref_2',
                'partner_country_id':self.country_france.id
            })

        tx=self.env['payment.transaction'].create({
            'acquirer_id':self.alipay.id,
            'amount':4,
            'currency_id':self.currency_yuan.id,
            'reference':'test_ref_2',
            'partner_country_id':self.country_france.id
        })
