#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
importtime
importrequests

fromwerkzeug.urlsimporturl_encode,url_join

fromflectraimport_,api,fields,models,tools
fromflectra.exceptionsimportAccessError,UserError

_logger=logging.getLogger(__name__)


classGoogleGmailMixin(models.AbstractModel):

    _name='google.gmail.mixin'
    _description='GoogleGmailMixin'

    _SERVICE_SCOPE='https://mail.google.com/'

    use_google_gmail_service=fields.Boolean('GmailAuthentication')
    google_gmail_authorization_code=fields.Char(string='AuthorizationCode',groups='base.group_system',copy=False)
    google_gmail_refresh_token=fields.Char(string='RefreshToken',groups='base.group_system',copy=False)
    google_gmail_access_token=fields.Char(string='AccessToken',groups='base.group_system',copy=False)
    google_gmail_access_token_expiration=fields.Integer(string='AccessTokenExpirationTimestamp',groups='base.group_system',copy=False)
    google_gmail_uri=fields.Char(compute='_compute_gmail_uri',string='URI',help='TheURLtogeneratetheauthorizationcodefromGoogle',groups='base.group_system')

    @api.depends('google_gmail_authorization_code')
    def_compute_gmail_uri(self):
        Config=self.env['ir.config_parameter'].sudo()
        google_gmail_client_id=Config.get_param('google_gmail_client_id')
        google_gmail_client_secret=Config.get_param('google_gmail_client_secret')
        base_url=self.get_base_url()

        redirect_uri=url_join(base_url,'/google_gmail/confirm')

        ifnotgoogle_gmail_client_idornotgoogle_gmail_client_secret:
            self.google_gmail_uri=False
        else:
            forrecordinself:
                google_gmail_uri='https://accounts.google.com/o/oauth2/v2/auth?%s'%url_encode({
                    'client_id':google_gmail_client_id,
                    'redirect_uri':redirect_uri,
                    'response_type':'code',
                    'scope':self._SERVICE_SCOPE,
                    #access_typeandpromptneededtogetarefreshtoken
                    'access_type':'offline',
                    'prompt':'consent',
                    'state':json.dumps({
                        'model':record._name,
                        'id':record.idorFalse,
                        'csrf_token':record._get_gmail_csrf_token()ifrecord.idelseFalse,
                    })
                })
                record.google_gmail_uri=google_gmail_uri

    defopen_google_gmail_uri(self):
        """OpentheURLtoaccepttheGmailpermission.

        Thisisdonewithanaction,sowecanforcetheuserthesavetheform.
        WeneedhimtosavetheformsothecurrentmailserverrecordexistinDB,and
        wecanincludetherecordIDintheURL.
        """
        self.ensure_one()

        ifnotself.env.user.has_group('base.group_system'):
            raiseAccessError(_('OnlytheadministratorcanlinkaGmailmailserver.'))

        ifnotself.google_gmail_uri:
            raiseUserError(_('PleaseconfigureyourGmailcredentials.'))

        return{
            'type':'ir.actions.act_url',
            'url':self.google_gmail_uri,
        }

    def_fetch_gmail_refresh_token(self,authorization_code):
        """Requesttherefreshtokenandtheinitialaccesstokenfromtheauthorizationcode.

        :return:
            refresh_token,access_token,access_token_expiration
        """
        response=self._fetch_gmail_token('authorization_code',code=authorization_code)

        return(
            response['refresh_token'],
            response['access_token'],
            int(time.time())+response['expires_in'],
        )

    def_fetch_gmail_access_token(self,refresh_token):
        """Refreshtheaccesstokenthankstotherefreshtoken.

        :return:
            access_token,access_token_expiration
        """
        response=self._fetch_gmail_token('refresh_token',refresh_token=refresh_token)

        return(
            response['access_token'],
            int(time.time())+response['expires_in'],
        )

    def_fetch_gmail_token(self,grant_type,**values):
        """Genericmethodtorequestanaccesstokenorarefreshtoken.

        ReturntheJSONresponseoftheGMailAPIandmanagetheerrorswhichcanoccur.

        :paramgrant_type:Dependstheactionwewanttodo(refresh_tokenorauthorization_code)
        :paramvalues:AdditionalparametersthatwillbegiventotheGMailendpoint
        """
        Config=self.env['ir.config_parameter'].sudo()
        google_gmail_client_id=Config.get_param('google_gmail_client_id')
        google_gmail_client_secret=Config.get_param('google_gmail_client_secret')
        base_url=self.get_base_url()
        redirect_uri=url_join(base_url,'/google_gmail/confirm')

        response=requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id':google_gmail_client_id,
                'client_secret':google_gmail_client_secret,
                'grant_type':grant_type,
                'redirect_uri':redirect_uri,
                **values,
            },
            timeout=5,
        )

        ifnotresponse.ok:
            raiseUserError(_('Anerroroccurredwhenfetchingtheaccesstoken.'))

        returnresponse.json()

    def_generate_oauth2_string(self,user,refresh_token):
        """GenerateaOAuth2stringwhichcanbeusedforauthentication.

        :paramuser:EmailaddressoftheGmailaccounttoauthenticate
        :paramrefresh_token:RefreshtokenforthegivenGmailaccount

        :return:TheSASLargumentfortheOAuth2mechanism.
        """
        self.ensure_one()
        now_timestamp=int(time.time())
        ifnotself.google_gmail_access_token\
           ornotself.google_gmail_access_token_expiration\
           orself.google_gmail_access_token_expiration<now_timestamp:

            access_token,expiration=self._fetch_gmail_access_token(self.google_gmail_refresh_token)

            self.write({
                'google_gmail_access_token':access_token,
                'google_gmail_access_token_expiration':expiration,
            })

            _logger.info(
                'GoogleGmail:fetchnewaccesstoken.Expiresin%iminutes',
                (self.google_gmail_access_token_expiration-now_timestamp)//60)
        else:
            _logger.info(
                'GoogleGmail:reuseexistingaccesstoken.Expirein%iminutes',
                (self.google_gmail_access_token_expiration-now_timestamp)//60)

        return'user=%s\1auth=Bearer%s\1\1'%(user,self.google_gmail_access_token)

    def_get_gmail_csrf_token(self):
        """GenerateaCSRFtokenthatwillbeverifiedin`google_gmail_callback`.

        Thiswillpreventamaliciouspersontomakeanadminuserdisconnectthemailservers.
        """
        self.ensure_one()
        _logger.info('GoogleGmail:generateCSRFtokenfor%s#%i',self._name,self.id)
        returntools.misc.hmac(
            env=self.env(su=True),
            scope='google_gmail_oauth',
            message=(self._name,self.id),
        )
