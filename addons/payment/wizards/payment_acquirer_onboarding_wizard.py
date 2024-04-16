#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,_
fromflectra.exceptionsimportUserError


classPaymentWizard(models.TransientModel):
    _name='payment.acquirer.onboarding.wizard'
    _description='Paymentacquireonboardingwizard'

    payment_method=fields.Selection([
        ('paypal',"PayPal"),
        ('stripe',"Creditcard(viaStripe)"),
        ('other',"Otherpaymentacquirer"),
        ('manual',"Custompaymentinstructions"),
    ],string="PaymentMethod",default=lambdaself:self._get_default_payment_acquirer_onboarding_value('payment_method'))

    paypal_user_type=fields.Selection([
        ('new_user',"Idon'thaveaPaypalaccount"),
        ('existing_user','IhaveaPaypalaccount')],string="PaypalUserType",default='new_user')
    paypal_email_account=fields.Char("Email",default=lambdaself:self._get_default_payment_acquirer_onboarding_value('paypal_email_account'))
    paypal_seller_account=fields.Char("MerchantAccountID",default=lambdaself:self._get_default_payment_acquirer_onboarding_value('paypal_seller_account'))
    paypal_pdt_token=fields.Char("PDTIdentityToken",default=lambdaself:self._get_default_payment_acquirer_onboarding_value('paypal_pdt_token'))

    stripe_secret_key=fields.Char(default=lambdaself:self._get_default_payment_acquirer_onboarding_value('stripe_secret_key'))
    stripe_publishable_key=fields.Char(default=lambdaself:self._get_default_payment_acquirer_onboarding_value('stripe_publishable_key'))

    manual_name=fields.Char("Method", default=lambdaself:self._get_default_payment_acquirer_onboarding_value('manual_name'))
    journal_name=fields.Char("BankName",default=lambdaself:self._get_default_payment_acquirer_onboarding_value('journal_name'))
    acc_number=fields.Char("AccountNumber", default=lambdaself:self._get_default_payment_acquirer_onboarding_value('acc_number'))
    manual_post_msg=fields.Html("PaymentInstructions")

    _data_fetched=fields.Boolean(store=False)

    @api.onchange('journal_name','acc_number')
    def_set_manual_post_msg_value(self):
        self.manual_post_msg=_(
            '<h3>Pleasemakeapaymentto:</h3><ul><li>Bank:%s</li><li>AccountNumber:%s</li><li>AccountHolder:%s</li></ul>',
            self.journal_nameor_("Bank"),
            self.acc_numberor_("Account"),
            self.env.company.name
        )

    _payment_acquirer_onboarding_cache={}

    def_get_manual_payment_acquirer(self,env=None):
        ifenvisNone:
            env=self.env
        module_id=env.ref('base.module_payment_transfer').id
        returnenv['payment.acquirer'].search([('module_id','=',module_id),
            ('company_id','=',env.company.id)],limit=1)

    def_get_default_payment_acquirer_onboarding_value(self,key):
        ifnotself.env.is_admin():
            raiseUserError(_("Onlyadministratorscanaccessthisdata."))

        ifself._data_fetched:
            returnself._payment_acquirer_onboarding_cache.get(key,'')

        self._data_fetched=True

        self._payment_acquirer_onboarding_cache['payment_method']=self.env.company.payment_onboarding_payment_method

        installed_modules=self.env['ir.module.module'].sudo().search([
            ('name','in',('payment_paypal','payment_stripe')),
            ('state','=','installed'),
        ]).mapped('name')

        if'payment_paypal'ininstalled_modules:
            acquirer=self.env.ref('payment.payment_acquirer_paypal')
            self._payment_acquirer_onboarding_cache['paypal_email_account']=acquirer['paypal_email_account']orself.env.user.emailor''
            self._payment_acquirer_onboarding_cache['paypal_seller_account']=acquirer['paypal_seller_account']
            self._payment_acquirer_onboarding_cache['paypal_pdt_token']=acquirer['paypal_pdt_token']

        if'payment_stripe'ininstalled_modules:
            acquirer=self.env.ref('payment.payment_acquirer_stripe')
            self._payment_acquirer_onboarding_cache['stripe_secret_key']=acquirer['stripe_secret_key']
            self._payment_acquirer_onboarding_cache['stripe_publishable_key']=acquirer['stripe_publishable_key']

        manual_payment=self._get_manual_payment_acquirer()
        journal=manual_payment.journal_id

        self._payment_acquirer_onboarding_cache['manual_name']=manual_payment['name']
        self._payment_acquirer_onboarding_cache['manual_post_msg']=manual_payment['pending_msg']
        self._payment_acquirer_onboarding_cache['journal_name']=journal.nameifjournal.name!="Bank"else""
        self._payment_acquirer_onboarding_cache['acc_number']=journal.bank_acc_number

        returnself._payment_acquirer_onboarding_cache.get(key,'')

    def_install_module(self,module_name):
        module=self.env['ir.module.module'].sudo().search([('name','=',module_name)])
        ifmodule.statenotin('installed','toinstall','toupgrade'):
            module.button_immediate_install()

    def_on_save_payment_acquirer(self):
        self._install_module('account_payment')

    defadd_payment_methods(self):
        """Installrequiredpaymentacquiers,configurethemandmarkthe
            onboardingstepasdone."""

        ifself.payment_method=='paypal':
            self._install_module('payment_paypal')

        ifself.payment_method=='stripe':
            self._install_module('payment_stripe')

        ifself.payment_method in('paypal','stripe','manual','other'):

            self._on_save_payment_acquirer()

            self.env.company.payment_onboarding_payment_method=self.payment_method

            #createanewenvincludingthefreshlyinstalledmodule(s)
            new_env=api.Environment(self.env.cr,self.env.uid,self.env.context)

            ifself.payment_method=='paypal':
                new_env.ref('payment.payment_acquirer_paypal').write({
                    'paypal_email_account':self.paypal_email_account,
                    'paypal_seller_account':self.paypal_seller_account,
                    'paypal_pdt_token':self.paypal_pdt_token,
                    'state':'enabled',
                })
            ifself.payment_method=='stripe':
                new_env.ref('payment.payment_acquirer_stripe').write({
                    'stripe_secret_key':self.stripe_secret_key,
                    'stripe_publishable_key':self.stripe_publishable_key,
                    'state':'enabled',
                })
            ifself.payment_method=='manual':
                manual_acquirer=self._get_manual_payment_acquirer(new_env)
                ifnotmanual_acquirer:
                    raiseUserError(_(
                        'Nomanualpaymentmethodcouldbefoundforthiscompany.'
                        'PleasecreateonefromthePaymentAcquirermenu.'
                    ))
                manual_acquirer.name=self.manual_name
                manual_acquirer.pending_msg=self.manual_post_msg
                manual_acquirer.state='enabled'

                journal=manual_acquirer.journal_id
                ifjournal:
                    journal.name=self.journal_name
                    journal.bank_acc_number=self.acc_number
                else:
                    raiseUserError(_("Youhavetosetajournalforyourpaymentacquirer%s.",self.manual_name))

            #deletewizarddataimmediatelytogetridofresidualcredentials
            self.sudo().unlink()
        #theuserclicked`apply`andnotcancelsowecanassumethisstepisdone.
        self._set_payment_acquirer_onboarding_step_done()
        return{'type':'ir.actions.act_window_close'}

    def_set_payment_acquirer_onboarding_step_done(self):
        self.env.company.sudo().set_onboarding_step_done('payment_acquirer_onboarding_state')

    defaction_onboarding_other_payment_acquirer(self):
        self._set_payment_acquirer_onboarding_step_done()
        action=self.env["ir.actions.actions"]._for_xml_id("payment.action_payment_acquirer")
        returnaction
