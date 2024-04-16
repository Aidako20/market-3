#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPaymentWizard(models.TransientModel):
    """Overrideforthesalequotationonboardingpanel."""

    _inherit='payment.acquirer.onboarding.wizard'
    _name='sale.payment.acquirer.onboarding.wizard'
    _description='SalePaymentacquireonboardingwizard'

    def_get_default_payment_method(self):
        returnself.env.company.sale_onboarding_payment_methodor'digital_signature'

    payment_method=fields.Selection(selection_add=[
        ('digital_signature',"Electronicsignature"),
        ('paypal',"PayPal"),
        ('stripe',"Creditcard(viaStripe)"),
        ('other',"Otherpaymentacquirer"),
        ('manual',"Custompaymentinstructions"),
    ],default=_get_default_payment_method)
    #

    def_set_payment_acquirer_onboarding_step_done(self):
        """Override."""
        self.env.company.sudo().set_onboarding_step_done('sale_onboarding_order_confirmation_state')

    defadd_payment_methods(self,*args,**kwargs):
        self.env.company.sale_onboarding_payment_method=self.payment_method
        ifself.payment_method=='digital_signature':
            self.env.company.portal_confirmation_sign=True
        ifself.payment_methodin('paypal','stripe','other','manual'):
            self.env.company.portal_confirmation_pay=True

        returnsuper(PaymentWizard,self).add_payment_methods(*args,**kwargs)
