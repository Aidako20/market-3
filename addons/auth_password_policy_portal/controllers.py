#-*-coding:utf-8-*-

fromflectra.httpimportrequest
fromflectra.addons.portal.controllers.portalimportCustomerPortal

classCustomerPortalPasswordPolicy(CustomerPortal):
    def_prepare_portal_layout_values(self):
        d=super()._prepare_portal_layout_values()
        d['password_minimum_length']=request.env['ir.config_parameter'].sudo().get_param('auth_password_policy.minlength')
        returnd
