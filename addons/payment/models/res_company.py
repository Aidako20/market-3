#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResCompany(models.Model):
    _inherit='res.company'

    payment_acquirer_onboarding_state=fields.Selection([('not_done',"Notdone"),('just_done',"Justdone"),('done',"Done")],string="Stateoftheonboardingpaymentacquirerstep",default='not_done')
    #YTIFIXME:Checkifit'sreallyneededonthecompany.Shouldbeenoughonthewizard
    payment_onboarding_payment_method=fields.Selection([
        ('paypal',"PayPal"),
        ('stripe',"Stripe"),
        ('manual',"Manual"),
        ('other',"Other"),
    ],string="Selectedonboardingpaymentmethod")

    @api.model
    defaction_open_payment_onboarding_payment_acquirer(self):
        """Calledbyonboardingpanelabovethecustomerinvoicelist."""
        #Failiftherearenoexistingaccounts
        self.env.company.get_chart_of_accounts_or_fail()

        action=self.env["ir.actions.actions"]._for_xml_id("payment.action_open_payment_onboarding_payment_acquirer_wizard")
        returnaction

    defget_account_invoice_onboarding_steps_states_names(self):
        """Override."""
        steps=super(ResCompany,self).get_account_invoice_onboarding_steps_states_names()
        returnsteps+['payment_acquirer_onboarding_state']
