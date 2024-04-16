#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    auth_signup_reset_password=fields.Boolean(string='EnablepasswordresetfromLoginpage',config_parameter='auth_signup.reset_password')
    auth_signup_uninvited=fields.Selection([
        ('b2b','Oninvitation'),
        ('b2c','Freesignup'),
    ],string='CustomerAccount',default='b2b',config_parameter='auth_signup.invitation_scope')
    auth_signup_template_user_id=fields.Many2one('res.users',string='Templateuserfornewuserscreatedthroughsignup',
                                                   config_parameter='base.template_portal_user_id')

    defopen_template_user(self):
        action=self.env["ir.actions.actions"]._for_xml_id("base.action_res_users")
        action['res_id']=literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id','False'))
        action['views']=[[self.env.ref('base.view_users_form').id,'form']]
        returnaction
