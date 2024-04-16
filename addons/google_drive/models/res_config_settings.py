#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"

    google_drive_authorization_code=fields.Char(string='AuthorizationCode',config_parameter='google_drive_authorization_code')
    google_drive_uri=fields.Char(compute='_compute_drive_uri',string='URI',help="TheURLtogeneratetheauthorizationcodefromGoogle")
    is_google_drive_token_generated=fields.Boolean(string='RefreshTokenGenerated')

    @api.depends('google_drive_authorization_code')
    def_compute_drive_uri(self):
        google_drive_uri=self.env['google.service']._get_google_token_uri('drive',scope=self.env['google.drive.config'].get_google_scope())
        forconfiginself:
            config.google_drive_uri=google_drive_uri

    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        refresh_token=self.env['ir.config_parameter'].sudo().get_param('google_drive_refresh_token',False)
        res.update(is_google_drive_token_generated=bool(refresh_token))
        returnres

    defconfirm_setup_token(self):
        params=self.env['ir.config_parameter'].sudo()
        authorization_code_before=params.get_param('google_drive_authorization_code')
        authorization_code=self.google_drive_authorization_code
        ifauthorization_code!=authorization_code_before:
            refresh_token=(
                self.env['google.service'].generate_refresh_token('drive',authorization_code)
                ifauthorization_codeelseFalse
            )
            params.set_param('google_drive_refresh_token',refresh_token)

    defaction_setup_token(self):
        self.ensure_one()
        ifself.env['google.drive.config']._module_deprecated():
            return

        template=self.env.ref('google_drive.google_drive_auth_code_wizard')
        return{
            'name':_('Setuprefreshtoken'),
            'type':'ir.actions.act_window',
            'res_model':'res.config.settings',
            'views':[(template.id,'form')],
            'target':'new',
        }
