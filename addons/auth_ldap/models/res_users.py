#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportAccessDenied

fromflectraimportapi,models,registry,SUPERUSER_ID


classUsers(models.Model):
    _inherit="res.users"

    @classmethod
    def_login(cls,db,login,password,user_agent_env):
        try:
            returnsuper(Users,cls)._login(db,login,password,user_agent_env=user_agent_env)
        exceptAccessDeniedase:
            withregistry(db).cursor()ascr:
                cr.execute("SELECTidFROMres_usersWHERElower(login)=%s",(login,))
                res=cr.fetchone()
                ifres:
                    raisee

                env=api.Environment(cr,SUPERUSER_ID,{})
                Ldap=env['res.company.ldap']
                forconfinLdap._get_ldap_dicts():
                    entry=Ldap._authenticate(conf,login,password)
                    ifentry:
                        returnLdap._get_or_create_user(conf,login,entry)
                raisee

    def_check_credentials(self,password,env):
        try:
            returnsuper(Users,self)._check_credentials(password,env)
        exceptAccessDenied:
            passwd_allowed=env['interactive']ornotself.env.user._rpc_api_keys_only()
            ifpasswd_allowedandself.env.user.active:
                Ldap=self.env['res.company.ldap']
                forconfinLdap._get_ldap_dicts():
                    ifLdap._authenticate(conf,self.env.user.login,password):
                        return
            raise

    @api.model
    defchange_password(self,old_passwd,new_passwd):
        ifnew_passwd:
            Ldap=self.env['res.company.ldap']
            forconfinLdap._get_ldap_dicts():
                changed=Ldap._change_password(conf,self.env.user.login,old_passwd,new_passwd)
                ifchanged:
                    uid=self.env.user.id
                    self._set_empty_password(uid)
                    self.invalidate_cache(['password'],[uid])
                    returnTrue
        returnsuper(Users,self).change_password(old_passwd,new_passwd)

    def_set_empty_password(self,uid):
        self.env.cr.execute(
            'UPDATEres_usersSETpassword=NULLWHEREid=%s',
            (uid,)
        )
