fromflectraimporthttp
fromflectra.httpimportrequest


classOnboardingController(http.Controller):

    @http.route('/account/account_invoice_onboarding',auth='user',type='json')
    defaccount_invoice_onboarding(self):
        """Returnsthe`banner`fortheaccountinvoiceonboardingpanel.
            Itcanbeemptyiftheuserhascloseditorifhedoesn'thave
            thepermissiontoseeit."""

        company=request.env.company
        ifnotrequest.env.is_admin()or\
                company.account_invoice_onboarding_state=='closed':
            return{}

        return{
            'html':request.env.ref('account.account_invoice_onboarding_panel')._render({
                'company':company,
                'state':company.get_and_update_account_invoice_onboarding_state()
            })
        }

    @http.route('/account/account_dashboard_onboarding',auth='user',type='json')
    defaccount_dashboard_onboarding(self):
        """Returnsthe`banner`fortheaccountdashboardonboardingpanel.
            Itcanbeemptyiftheuserhascloseditorifhedoesn'thave
            thepermissiontoseeit."""
        company=request.env.company

        ifnotrequest.env.is_admin()or\
                company.account_dashboard_onboarding_state=='closed':
            return{}

        return{
            'html':request.env.ref('account.account_dashboard_onboarding_panel')._render({
                'company':company,
                'state':company.get_and_update_account_dashboard_onboarding_state()
            })
        }
