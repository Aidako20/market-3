#-*-coding:utf-8-*-
importbase64
importfunctools
importhmac
importio
importlogging
importos
importre
importstruct
importtime

importwerkzeug.urls

fromflectraimport_,api,fields,models
fromflectra.addons.base.models.res_usersimportcheck_identity
fromflectra.exceptionsimportAccessDenied,UserError
fromflectra.httpimportrequest,db_list
fromflectra.toolsimportsql

_logger=logging.getLogger(__name__)

TRUSTED_DEVICE_SCOPE='2fa_trusted_device'

compress=functools.partial(re.sub,r'\s','')
classUsers(models.Model):
    _inherit='res.users'

    totp_secret=fields.Char(copy=False,groups=fields.NO_ACCESS,compute='_compute_totp_secret',inverse='_inverse_totp_secret')
    totp_enabled=fields.Boolean(string="Two-factorauthentication",compute='_compute_totp_enabled',search='_search_totp_enable')
    totp_trusted_device_ids=fields.One2many('res.users.apikeys','user_id',
        string="TrustedDevices",domain=[('scope','=',TRUSTED_DEVICE_SCOPE)])
    api_key_ids=fields.One2many(domain=[('scope','!=',TRUSTED_DEVICE_SCOPE)])

    def__init__(self,pool,cr):
        init_res=super().__init__(pool,cr)
        ifnotsql.column_exists(cr,self._table,"totp_secret"):
            cr.execute("ALTERTABLEres_usersADDCOLUMNtotp_secretvarchar")
        pool[self._name].SELF_READABLE_FIELDS=self.SELF_READABLE_FIELDS+['totp_enabled','totp_trusted_device_ids']
        returninit_res

    def_mfa_type(self):
        r=super()._mfa_type()
        ifrisnotNone:
            returnr
        ifself.totp_enabled:
            return'totp'

    def_mfa_url(self):
        r=super()._mfa_url()
        ifrisnotNone:
            returnr
        ifself._mfa_type()=='totp':
            return'/web/login/totp'

    @api.depends('totp_secret')
    def_compute_totp_enabled(self):
        forr,vinzip(self,self.sudo()):
            r.totp_enabled=bool(v.totp_secret)

    def_rpc_api_keys_only(self):
        #2FAenabledmeanswecan'tallowpassword-basedRPC
        self.ensure_one()
        returnself.totp_enabledorsuper()._rpc_api_keys_only()

    def_get_session_token_fields(self):
        returnsuper()._get_session_token_fields()|{'totp_secret'}

    def_totp_check(self,code):
        sudo=self.sudo()
        key=base64.b32decode(sudo.totp_secret)
        match=TOTP(key).match(code)
        ifmatchisNone:
            _logger.info("2FAcheck:FAILfor%s%r",self,sudo.login)
            raiseAccessDenied()
        _logger.info("2FAcheck:SUCCESSfor%s%r",self,sudo.login)

    def_totp_try_setting(self,secret,code):
        ifself.totp_enabledorself!=self.env.user:
            _logger.info("2FAenable:REJECTfor%s%r",self,self.login)
            returnFalse

        secret=compress(secret).upper()
        match=TOTP(base64.b32decode(secret)).match(code)
        ifmatchisNone:
            _logger.info("2FAenable:REJECTCODEfor%s%r",self,self.login)
            returnFalse

        self.sudo().totp_secret=secret
        ifrequest:
            self.flush()
            #updatesessiontokensotheuserdoesnotgetloggedout(cacheclearedbychange)
            new_token=self.env.user._compute_session_token(request.session.sid)
            request.session.session_token=new_token

        _logger.info("2FAenable:SUCCESSfor%s%r",self,self.login)
        returnTrue

    @check_identity
    deftotp_disable(self):
        logins=','.join(map(repr,self.mapped('login')))
        ifnot(self==self.env.userorself.env.user._is_admin()orself.env.su):
            _logger.info("2FAdisable:REJECTfor%s(%s)byuid#%s",self,logins,self.env.user.id)
            returnFalse

        self.revoke_all_devices()
        self.sudo().write({'totp_secret':False})

        ifrequestandself==self.env.user:
            self.flush()
            #updatesessiontokensotheuserdoesnotgetloggedout(cacheclearedbychange)
            new_token=self.env.user._compute_session_token(request.session.sid)
            request.session.session_token=new_token

        _logger.info("2FAdisable:SUCCESSfor%s(%s)byuid#%s",self,logins,self.env.user.id)
        return{
            'type':'ir.actions.client',
            'tag':'display_notification',
            'params':{
                'type':'warning',
                'message':_("Two-factorauthenticationdisabledforuser(s)%s",logins),
                'next':{'type':'ir.actions.act_window_close'},
            }
        }

    @check_identity
    deftotp_enable_wizard(self):
        ifself.env.user!=self:
            raiseUserError(_("Two-factorauthenticationcanonlybeenabledforyourself"))

        ifself.totp_enabled:
            raiseUserError(_("Two-factorauthenticationalreadyenabled"))

        secret_bytes_count=TOTP_SECRET_SIZE//8
        secret=base64.b32encode(os.urandom(secret_bytes_count)).decode()
        #formatsecretingroupsof4charactersforreadability
        secret=''.join(map(''.join,zip(*[iter(secret)]*4)))
        w=self.env['auth_totp.wizard'].create({
            'user_id':self.id,
            'secret':secret,
        })
        return{
            'type':'ir.actions.act_window',
            'target':'new',
            'res_model':'auth_totp.wizard',
            'name':_("EnableTwo-FactorAuthentication"),
            'res_id':w.id,
            'views':[(False,'form')],
        }

    @check_identity
    defrevoke_all_devices(self):
        self._revoke_all_devices()

    def_revoke_all_devices(self):
        self.totp_trusted_device_ids._remove()

    @api.model
    defchange_password(self,old_passwd,new_passwd):
        self.env.user._revoke_all_devices()
        returnsuper().change_password(old_passwd,new_passwd)

    def_compute_totp_secret(self):
        foruserinself.filtered('id'):
            self.env.cr.execute('SELECTtotp_secretFROMres_usersWHEREid=%s',(user.id,))
            user.totp_secret=self.env.cr.fetchone()[0]

    def_inverse_totp_secret(self):
        foruserinself.filtered('id'):
            secret=user.totp_secretifuser.totp_secretelseNone
            self.env.cr.execute('UPDATEres_usersSETtotp_secret=%sWHEREid=%s',(secret,user.id))

    def_search_totp_enable(self,operator,value):
        value=notvalueifoperator=='!='elsevalue
        ifvalue:
            self.env.cr.execute("SELECTidFROMres_usersWHEREtotp_secretISNOTNULL")
        else:
            self.env.cr.execute("SELECTidFROMres_usersWHEREtotp_secretISNULLORtotp_secret='false'")
        result=self.env.cr.fetchall()
        return[('id','in',[x[0]forxinresult])]

classTOTPWizard(models.TransientModel):
    _name='auth_totp.wizard'
    _description="Two-FactorSetupWizard"

    user_id=fields.Many2one('res.users',required=True,readonly=True)
    secret=fields.Char(required=True,readonly=True)
    url=fields.Char(store=True,readonly=True,compute='_compute_qrcode')
    qrcode=fields.Binary(
        attachment=False,store=True,readonly=True,
        compute='_compute_qrcode',
    )
    code=fields.Char(string="VerificationCode",size=7)

    @api.depends('user_id.login','user_id.company_id.display_name','secret')
    def_compute_qrcode(self):
        #TODO:make"issuer"configurablethroughconfigparameter?
        global_issuer=requestandrequest.httprequest.host.split(':',1)[0]
        forwinself:
            issuer=global_issuerorw.user_id.company_id.display_name
            w.url=url=werkzeug.urls.url_unparse((
                'otpauth','totp',
                werkzeug.urls.url_quote(f'{issuer}:{w.user_id.login}',safe=':'),
                werkzeug.urls.url_encode({
                    'secret':compress(w.secret),
                    'issuer':issuer,
                    #apparentlyalowercasehashnameisanathematogoogle
                    #authenticator(error)andpasslib(notoken)
                    'algorithm':ALGORITHM.upper(),
                    'digits':DIGITS,
                    'period':TIMESTEP,
                }),''
            ))

            data=io.BytesIO()
            importqrcode
            qrcode.make(url.encode(),box_size=4).save(data,optimise=True,format='PNG')
            w.qrcode=base64.b64encode(data.getvalue()).decode()

    @check_identity
    defenable(self):
        try:
            c=int(compress(self.code))
        exceptValueError:
            raiseUserError(_("Theverificationcodeshouldonlycontainnumbers"))
        ifself.user_id._totp_try_setting(self.secret,c):
            self.secret=''#emptyit,becausewhykeepituntilGC?
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                    'type':'success',
                    'message':_("Two-factorauthenticationisnowenabled."),
                    'next':{'type':'ir.actions.act_window_close'},
                }
            }
        raiseUserError(_('Verificationfailed,pleasedouble-checkthe6-digitcode'))

#160bits,asrecommendedbyHOTPRFC4226,section4,R6.
#GoogleAuthuses80bitsbydefaultbutsupports160.
TOTP_SECRET_SIZE=160

#Thealgorithm(andkeyURIformat)allowscustomisingtheseparametersbut
#googleauthenticatordoesn'tsupportit
#https://github.com/google/google-authenticator/wiki/Key-Uri-Format
ALGORITHM='sha1'
DIGITS=6
TIMESTEP=30

classTOTP:
    def__init__(self,key):
        self._key=key

    defmatch(self,code,t=None,window=TIMESTEP):
        """
        :paramcode:authenticatorcodetocheckagainstthiskey
        :paramintt:currenttimestamp(seconds)
        :paramintwindow:fuzzwindowtoaccountforslowfingers,network
                           latency,desynchronisedclocks,...,everycode
                           validbetweent-windowant+windowisconsidered
                           valid
        """
        iftisNone:
            t=time.time()

        low=int((t-window)/TIMESTEP)
        high=int((t+window)/TIMESTEP)+1

        returnnext((
            counterforcounterinrange(low,high)
            ifhotp(self._key,counter)==code
        ),None)

defhotp(secret,counter):
    #Cisthe64bcounterencodedinbig-endian
    C=struct.pack(">Q",counter)
    mac=hmac.new(secret,msg=C,digestmod=ALGORITHM).digest()
    #thedataoffsetisthelastnibbleofthehash
    offset=mac[-1]&0xF
    #codeisthe4bytesattheoffsetinterpretedasa31bbig-endianuint
    #(31btoavoidsignconcerns).Thiseffectivelylimitsdigitsto9and
    #hard-limitsitto10:eachdigitisnormallyworth3.32bitsbutthe
    #10thisonlyworth1.1(9digitsencode29.9bits).
    code=struct.unpack_from('>I',mac,offset)[0]&0x7FFFFFFF
    r=code%(10**DIGITS)
    #NOTE:usetext/bytesinsteadofint?
    returnr
