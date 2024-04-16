#-*-coding:utf-8-*-
fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError


classResUsers(models.Model):
    _inherit='res.users'

    @api.model
    defget_password_policy(self):
        params=self.env['ir.config_parameter'].sudo()
        return{
            'minlength':int(params.get_param('auth_password_policy.minlength',default=0)),
        }

    def_set_password(self):
        self._check_password_policy(self.mapped('password'))

        super(ResUsers,self)._set_password()

    def_check_password_policy(self,passwords):
        failures=[]
        params=self.env['ir.config_parameter'].sudo()

        minlength=int(params.get_param('auth_password_policy.minlength',default=0))
        forpasswordinpasswords:
            ifnotpassword:
                continue
            iflen(password)<minlength:
                failures.append(_(u"Passwordsmusthaveatleast%dcharacters,got%d.")%(minlength,len(password)))

        iffailures:
            raiseUserError(u'\n\n'.join(failures))
