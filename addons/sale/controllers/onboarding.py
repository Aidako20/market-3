#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classOnboardingController(http.Controller):

    @http.route('/sales/sale_quotation_onboarding_panel',auth='user',type='json')
    defsale_quotation_onboarding(self):
        """Returnsthe`banner`forthesaleonboardingpanel.
            Itcanbeemptyiftheuserhascloseditorifhedoesn'thave
            thepermissiontoseeit."""

        company=request.env.company
        ifnotrequest.env.is_admin()or\
           company.sale_quotation_onboarding_state=='closed':
            return{}

        return{
            'html':request.env.ref('sale.sale_quotation_onboarding_panel')._render({
                'company':company,
                'state':company.get_and_update_sale_quotation_onboarding_state()
            })
        }
