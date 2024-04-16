#-*-coding:utf-8-*-

fromflectra.httpimportrequest
fromflectra.addons.auth_signup.controllers.mainimportAuthSignupHome

classAddPolicyData(AuthSignupHome):
    defget_auth_signup_config(self):
        d=super(AddPolicyData,self).get_auth_signup_config()
        d['password_minimum_length']=request.env['ir.config_parameter'].sudo().get_param('auth_password_policy.minlength')
        returnd
