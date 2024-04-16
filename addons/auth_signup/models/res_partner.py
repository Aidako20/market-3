#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importrandom
importwerkzeug.urls

fromcollectionsimportdefaultdict
fromdatetimeimportdatetime,timedelta

fromflectraimportapi,exceptions,fields,models,_
fromflectra.toolsimportsql
classSignupError(Exception):
    pass

defrandom_token():
    #thetokenhasanentropyofabout120bits(6bits/char*20chars)
    chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return''.join(random.SystemRandom().choice(chars)for_inrange(20))

defnow(**kwargs):
    returndatetime.now()+timedelta(**kwargs)


classResPartner(models.Model):
    _inherit='res.partner'

    signup_token=fields.Char(copy=False,groups="base.group_erp_manager",compute='_compute_token',inverse='_inverse_token')
    signup_type=fields.Char(string='SignupTokenType',copy=False,groups="base.group_erp_manager")
    signup_expiration=fields.Datetime(copy=False,groups="base.group_erp_manager")
    signup_valid=fields.Boolean(compute='_compute_signup_valid',string='SignupTokenisValid')
    signup_url=fields.Char(compute='_compute_signup_url',string='SignupURL')

    definit(self):
        super().init()
        ifnotsql.column_exists(self.env.cr,self._table,"signup_token"):
            self.env.cr.execute("ALTERTABLEres_partnerADDCOLUMNsignup_tokenvarchar")

    @api.depends('signup_token','signup_expiration')
    def_compute_signup_valid(self):
        dt=now()
        forpartner,partner_sudoinzip(self,self.sudo()):
            partner.signup_valid=bool(partner_sudo.signup_token)and\
            (notpartner_sudo.signup_expirationordt<=partner_sudo.signup_expiration)

    def_compute_signup_url(self):
        """proxyforfunctionfieldtowardsactualimplementation"""
        result=self.sudo()._get_signup_url_for_action()
        forpartnerinself:
            ifany(u.has_group('base.group_user')foruinpartner.user_idsifu!=self.env.user):
                self.env['res.users'].check_access_rights('write')
            ifany(u.has_group('base.group_portal')foruinpartner.user_idsifu!=self.env.user):
                self.env['res.partner'].check_access_rights('write')
            partner.signup_url=result.get(partner.id,False)

    def_compute_token(self):
        forpartnerinself.filtered('id'):
            self.env.cr.execute('SELECTsignup_tokenFROMres_partnerWHEREid=%s',(partner._origin.id,))
            partner.signup_token=self.env.cr.fetchone()[0]

    def_inverse_token(self):
        forpartnerinself.filtered('id'):
            self.env.cr.execute('UPDATEres_partnerSETsignup_token=%sWHEREid=%s',(partner.signup_tokenorNone,partner.id))

    def_get_signup_url_for_action(self,url=None,action=None,view_type=None,menu_id=None,res_id=None,model=None):
        """generateasignupurlforthegivenpartneridsandaction,possiblyoverriding
            theurlstatecomponents(menu_id,id,view_type)"""

        res=dict.fromkeys(self.ids,False)
        forpartnerinself:
            base_url=partner.get_base_url()
            #whenrequired,makesurethepartnerhasavalidsignuptoken
            ifself.env.context.get('signup_valid')andnotpartner.user_ids:
                partner.sudo().signup_prepare()

            route='login'
            #theparameterstoencodeforthequery
            query=dict(db=self.env.cr.dbname)
            signup_type=self.env.context.get('signup_force_type_in_url',partner.sudo().signup_typeor'')
            ifsignup_type:
                route='reset_password'ifsignup_type=='reset'elsesignup_type

            ifpartner.sudo().signup_tokenandsignup_type:
                query['token']=partner.sudo().signup_token
            elifpartner.user_ids:
                query['login']=partner.user_ids[0].login
            else:
                continue       #nosignuptoken,nouser,thusnosignupurl!

            ifurl:
                query['redirect']=url
            else:
                fragment=dict()
                base='/web#'
                ifaction=='/mail/view':
                    base='/mail/view?'
                elifaction:
                    fragment['action']=action
                ifview_type:
                    fragment['view_type']=view_type
                ifmenu_id:
                    fragment['menu_id']=menu_id
                ifmodel:
                    fragment['model']=model
                ifres_id:
                    fragment['res_id']=res_id

                iffragment:
                    query['redirect']=base+werkzeug.urls.url_encode(fragment)

            signup_url="/web/%s?%s"%(route,werkzeug.urls.url_encode(query))
            ifnotself.env.context.get('relative_url'):
                signup_url=werkzeug.urls.url_join(base_url,signup_url)
            res[partner.id]=signup_url

        returnres

    defaction_signup_prepare(self):
        returnself.signup_prepare()

    defsignup_get_auth_param(self):
        """Getasignuptokenrelatedtothepartnerifsignupisenabled.
            Ifthepartneralreadyhasauser,gettheloginparameter.
        """
        ifnotself.env.user.has_group('base.group_user')andnotself.env.is_admin():
            raiseexceptions.AccessDenied()

        res=defaultdict(dict)

        allow_signup=self.env['res.users']._get_signup_invitation_scope()=='b2c'
        forpartnerinself:
            partner=partner.sudo()
            ifallow_signupandnotpartner.user_ids:
                partner.signup_prepare()
                res[partner.id]['auth_signup_token']=partner.signup_token
            elifpartner.user_ids:
                res[partner.id]['auth_login']=partner.user_ids[0].login
        returnres

    defsignup_cancel(self):
        returnself.write({'signup_token':False,'signup_type':False,'signup_expiration':False})

    defsignup_prepare(self,signup_type="signup",expiration=False):
        """generateanewtokenforthepartnerswiththegivenvalidity,ifnecessary
            :paramexpiration:theexpirationdatetimeofthetoken(string,optional)
        """
        forpartnerinself:
            ifexpirationornotpartner.signup_valid:
                token=random_token()
                whileself._signup_retrieve_partner(token):
                    token=random_token()
                partner.write({'signup_token':token,'signup_type':signup_type,'signup_expiration':expiration})
        returnTrue

    @api.model
    def_signup_retrieve_partner(self,token,check_validity=False,raise_exception=False):
        """findthepartnercorrespondingtoatoken,andpossiblycheckitsvalidity
            :paramtoken:thetokentoresolve
            :paramcheck_validity:ifTrue,alsocheckvalidity
            :paramraise_exception:ifTrue,raiseexceptioninsteadofreturningFalse
            :return:partner(browserecord)orFalse(ifraise_exceptionisFalse)
        """
        self.env.cr.execute("SELECTidFROMres_partnerWHEREsignup_token=%sANDactive",(token,))
        partner_id=self.env.cr.fetchone()
        partner=self.browse(partner_id[0])ifpartner_idelseNone
        ifnotpartner:
            ifraise_exception:
                raiseexceptions.UserError(_("Signuptoken'%s'isnotvalid",token))
            returnFalse
        ifcheck_validityandnotpartner.signup_valid:
            ifraise_exception:
                raiseexceptions.UserError(_("Signuptoken'%s'isnolongervalid",token))
            returnFalse
        returnpartner

    @api.model
    defsignup_retrieve_info(self,token):
        """retrievetheuserinfoaboutthetoken
            :return:adictionarywiththeuserinformation:
                -'db':thenameofthedatabase
                -'token':thetoken,iftokenisvalid
                -'name':thenameofthepartner,iftokenisvalid
                -'login':theuserlogin,iftheuseralreadyexists
                -'email':thepartneremail,iftheuserdoesnotexist
        """
        partner=self._signup_retrieve_partner(token,raise_exception=True)
        res={'db':self.env.cr.dbname}
        ifpartner.signup_valid:
            res['token']=token
            res['name']=partner.name
        ifpartner.user_ids:
            res['login']=partner.user_ids[0].login
        else:
            res['email']=res['login']=partner.emailor''
        returnres
