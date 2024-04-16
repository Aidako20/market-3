fromflectraimportapi,fields,models,_


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    minlength=fields.Integer("MinimumPasswordLength",help="Minimumnumberofcharacterspasswordsmustcontain,setto0todisable.")

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()

        res['minlength']=int(self.env['ir.config_parameter'].sudo().get_param('auth_password_policy.minlength',default=0))

        returnres

    @api.model
    defset_values(self):
        self.env['ir.config_parameter'].sudo().set_param('auth_password_policy.minlength',self.minlength)

        super(ResConfigSettings,self).set_values()

    @api.onchange('minlength')
    def_on_change_mins(self):
        """Passwordlowerboundsmustbenaturals
        """
        self.minlength=max(0,self.minlengthor0)
