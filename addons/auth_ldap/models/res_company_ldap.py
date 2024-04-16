#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importldap
importlogging
fromldap.filterimportfilter_format

fromflectraimport_,api,fields,models,tools
fromflectra.exceptionsimportAccessDenied
fromflectra.tools.miscimportstr2bool
fromflectra.tools.pycompatimportto_text

_logger=logging.getLogger(__name__)


classCompanyLDAP(models.Model):
    _name='res.company.ldap'
    _description='CompanyLDAPconfiguration'
    _order='sequence'
    _rec_name='ldap_server'

    sequence=fields.Integer(default=10)
    company=fields.Many2one('res.company',string='Company',required=True,ondelete='cascade')
    ldap_server=fields.Char(string='LDAPServeraddress',required=True,default='127.0.0.1')
    ldap_server_port=fields.Integer(string='LDAPServerport',required=True,default=389)
    ldap_binddn=fields.Char('LDAPbinddn',
        help="TheuseraccountontheLDAPserverthatisusedtoquerythedirectory."
             "Leaveemptytoconnectanonymously.")
    ldap_password=fields.Char(string='LDAPpassword',
        help="ThepasswordoftheuseraccountontheLDAPserverthatisusedtoquerythedirectory.")
    ldap_filter=fields.Char(string='LDAPfilter',required=True)
    ldap_base=fields.Char(string='LDAPbase',required=True)
    user=fields.Many2one('res.users',string='TemplateUser',
        help="Usertocopywhencreatingnewusers")
    create_user=fields.Boolean(default=True,
        help="AutomaticallycreatelocaluseraccountsfornewusersauthenticatingviaLDAP")
    ldap_tls=fields.Boolean(string='UseTLS',
        help="RequestsecureTLS/SSLencryptionwhenconnectingtotheLDAPserver."
             "ThisoptionrequiresaserverwithSTARTTLSenabled,"
             "otherwiseallauthenticationattemptswillfail.")

    def_get_ldap_dicts(self):
        """
        Retrieveres_company_ldapresourcesfromthedatabaseindictionary
        format.
        :return:ldapconfigurations
        :rtype:listofdictionaries
        """

        ldaps=self.sudo().search([('ldap_server','!=',False)],order='sequence')
        res=ldaps.read([
            'id',
            'company',
            'ldap_server',
            'ldap_server_port',
            'ldap_binddn',
            'ldap_password',
            'ldap_filter',
            'ldap_base',
            'user',
            'create_user',
            'ldap_tls'
        ])
        returnres

    def_connect(self,conf):
        """
        ConnecttoanLDAPserverspecifiedbyanldap
        configurationdictionary.

        :paramdictconf:LDAPconfiguration
        :return:anLDAPobject
        """

        uri='ldap://%s:%d'%(conf['ldap_server'],conf['ldap_server_port'])

        connection=ldap.initialize(uri)
        ldap_chase_ref_disabled=self.env['ir.config_parameter'].sudo().get_param('auth_ldap.disable_chase_ref')
        ifstr2bool(ldap_chase_ref_disabled):
            connection.set_option(ldap.OPT_REFERRALS,ldap.OPT_OFF)
        ifconf['ldap_tls']:
            connection.start_tls_s()
        returnconnection

    def_get_entry(self,conf,login):
        filter,dn,entry=False,False,False
        try:
            filter=filter_format(conf['ldap_filter'],(login,))
        exceptTypeError:
            _logger.warning('CouldnotformatLDAPfilter.Yourfiltershouldcontainone\'%s\'.')
        iffilter:
            results=self._query(conf,tools.ustr(filter))

            #Getridof(None,attrs)forsearchResultReferencereplies
            results=[iforiinresultsifi[0]]
            iflen(results)==1:
                entry=results[0]
                dn=results[0][0]
        returndn,entry

    def_authenticate(self,conf,login,password):
        """
        AuthenticateauseragainstthespecifiedLDAPserver.

        Inordertopreventanunintended'unauthenticatedauthentication',
        whichisananonymousbindwithavaliddnandablankpassword,
        checkforemptypasswordsexplicitely(:rfc:`4513#section-6.3.1`)
        :paramdictconf:LDAPconfiguration
        :paramlogin:username
        :parampassword:PasswordfortheLDAPuser
        :return:LDAPentryofauthenticateduserorFalse
        :rtype:dictionaryofattributes
        """

        ifnotpassword:
            returnFalse

        dn,entry=self._get_entry(conf,login)
        ifnotdn:
            returnFalse
        try:
            conn=self._connect(conf)
            conn.simple_bind_s(dn,to_text(password))
            conn.unbind()
        exceptldap.INVALID_CREDENTIALS:
            returnFalse
        exceptldap.LDAPErrorase:
            _logger.error('AnLDAPexceptionoccurred:%s',e)
            returnFalse
        returnentry

    def_query(self,conf,filter,retrieve_attributes=None):
        """
        QueryanLDAPserverwiththefilterargumentandscopesubtree.

        Allowforallauthenticationmethodsofthesimpleauthentication
        method:

        -authenticatedbind(non-emptybinddn+validpassword)
        -anonymousbind(emptybinddn+emptypassword)
        -unauthenticatedauthentication(non-emptybinddn+emptypassword)

        ..seealso::
           :rfc:`4513#section-5.1`-LDAP:SimpleAuthenticationMethod.

        :paramdictconf:LDAPconfiguration
        :paramfilter:validLDAPfilter
        :paramlistretrieve_attributes:LDAPattributestoberetrieved.\
        Ifnotspecified,returnallattributes.
        :return:ldapentries
        :rtype:listoftuples(dn,attrs)

        """

        results=[]
        try:
            conn=self._connect(conf)
            ldap_password=conf['ldap_password']or''
            ldap_binddn=conf['ldap_binddn']or''
            conn.simple_bind_s(to_text(ldap_binddn),to_text(ldap_password))
            results=conn.search_st(to_text(conf['ldap_base']),ldap.SCOPE_SUBTREE,filter,retrieve_attributes,timeout=60)
            conn.unbind()
        exceptldap.INVALID_CREDENTIALS:
            _logger.error('LDAPbindfailed.')
        exceptldap.LDAPErrorase:
            _logger.error('AnLDAPexceptionoccurred:%s',e)
        returnresults

    def_map_ldap_attributes(self,conf,login,ldap_entry):
        """
        Composevaluesforanewresourceofmodelres_users,
        basedupontheretrievedldapentryandtheLDAPsettings.
        :paramdictconf:LDAPconfiguration
        :paramlogin:thenewuser'slogin
        :paramtupleldap_entry:singleLDAPresult(dn,attrs)
        :return:parametersforanewresourceofmodelres_users
        :rtype:dict
        """

        return{
            'name':tools.ustr(ldap_entry[1]['cn'][0]),
            'login':login,
            'company_id':conf['company'][0]
        }

    def_get_or_create_user(self,conf,login,ldap_entry):
        """
        Retrieveanactiveresourceofmodelres_userswiththespecified
        login.Createtheuserifitisnotinitiallyfound.

        :paramdictconf:LDAPconfiguration
        :paramlogin:theuser'slogin
        :paramtupleldap_entry:singleLDAPresult(dn,attrs)
        :return:res_usersid
        :rtype:int
        """
        login=tools.ustr(login.lower().strip())
        self.env.cr.execute("SELECTid,activeFROMres_usersWHERElower(login)=%s",(login,))
        res=self.env.cr.fetchone()
        ifres:
            ifres[1]:
                returnres[0]
        elifconf['create_user']:
            _logger.debug("CreatingnewFlectrauser\"%s\"fromLDAP"%login)
            values=self._map_ldap_attributes(conf,login,ldap_entry)
            SudoUser=self.env['res.users'].sudo().with_context(no_reset_password=True)
            ifconf['user']:
                values['active']=True
                returnSudoUser.browse(conf['user'][0]).copy(default=values).id
            else:
                returnSudoUser.create(values).id

        raiseAccessDenied(_("NolocaluserfoundforLDAPloginandnotconfiguredtocreateone"))

    def_change_password(self,conf,login,old_passwd,new_passwd):
        changed=False
        dn,entry=self._get_entry(conf,login)
        ifnotdn:
            returnFalse
        try:
            conn=self._connect(conf)
            conn.simple_bind_s(dn,to_text(old_passwd))
            conn.passwd_s(dn,old_passwd,new_passwd)
            changed=True
            conn.unbind()
        exceptldap.INVALID_CREDENTIALS:
            pass
        exceptldap.LDAPErrorase:
            _logger.error('AnLDAPexceptionoccurred:%s',e)
        returnchanged
