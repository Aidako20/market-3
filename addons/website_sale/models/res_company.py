#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResCompany(models.Model):
    _inherit='res.company'

    website_sale_onboarding_payment_acquirer_state=fields.Selection([('not_done',"Notdone"),('just_done',"Justdone"),('done',"Done")],string="Stateofthewebsitesaleonboardingpaymentacquirerstep",default='not_done')

    @api.model
    defaction_open_website_sale_onboarding_payment_acquirer(self):
        """Calledbyonboardingpanelabovethequotationlist."""
        self.env.company.get_chart_of_accounts_or_fail()
        action=self.env["ir.actions.actions"]._for_xml_id("website_sale.action_open_website_sale_onboarding_payment_acquirer_wizard")
        returnaction
