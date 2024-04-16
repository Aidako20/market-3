#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classPaymentWizard(models.TransientModel):
    _inherit='payment.acquirer.onboarding.wizard'
    _name='website.sale.payment.acquirer.onboarding.wizard'
    _description='WebsitePaymentacquireonboardingwizard'

    def_set_payment_acquirer_onboarding_step_done(self):
        """Override."""
        self.env.company.sudo().set_onboarding_step_done('website_sale_onboarding_payment_acquirer_state')
