#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
importtime
importrequests

fromwerkzeug.urlsimporturl_encode,url_join

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportAccessError,UserError
fromflectra.tools.miscimporthmac

_logger=logging.getLogger(__name__)


classMicrosoftOutlookMixin(models.AbstractModel):

    _name='microsoft.outlook.mixin'
    _description='MicrosoftOutlookMixin'

    _OUTLOOK_SCOPE=None

    use_microsoft_outlook_service=fields.Boolean('OutlookAuthentication')
    is_microsoft_outlook_configured=fields.Boolean('IsOutlookCredentialConfigured',
        compute='_compute_is_microsoft_outlook_configured')
    microsoft_outlook_refresh_token=fields.Char(string='OutlookRefreshToken',
        groups='base.group_system',copy=False)
    microsoft_outlook_access_token=fields.Char(string='OutlookAccessToken',
        groups='base.group_system',copy=False)
    microsoft_outlook_access_token_expiration=fields.Integer(string='OutlookAccessTokenExpirationTimestamp',
        groups='base.group_system',copy=False)
    microsoft_outlook_uri=fields.Char(compute='_compute_outlook_uri',string='AuthenticationURI',
        help='TheURLtogeneratetheauthorizationcodefromOutlook',groups='base.group_system')

    @api.depends('use_microsoft_outlook_service')
    def_compute_is_microsoft_outlook_configured(self):
        Config=self.env['ir.config_parameter'].sudo()
        microsoft_outlook_client_id=Config.get_param('microsoft_outlook_client_id')
        microsoft_outlook_client_secret=Config.get_param('microsoft_outlook_client_secret')
        self.is_microsoft_outlook_configured=microsoft_outlook_client_idandmicrosoft_outlook_client_secret

    @api.depends('use_microsoft_outlook_service')
    def_compute_outlook_uri(self):
        Config=self.env['ir.config_parameter'].sudo()
        base_url=self.get_base_url()
        microsoft_outlook_client_id=Config.get_param('microsoft_outlook_client_id')

        forrecordinself:
            ifnotrecord.idornotrecord.use_microsoft_outlook_serviceornotrecord.is_microsoft_outlook_configured:
                record.microsoft_outlook_uri=False
                continue

            record.microsoft_outlook_uri=url_join(self._get_microsoft_endpoint(),'authorize?%s'%url_encode({
                'client_id':microsoft_outlook_client_id,
                'response_type':'code',
                'redirect_uri':url_join(base_url,'/microsoft_outlook/confirm'),
                'response_mode':'query',
                #offline_accessisneededtohavetherefresh_token
                'scope':'offline_access%s'%self._OUTLOOK_SCOPE,
                'state':json.dumps({
                    'model':record._name,
                    'id':record.id,
                    'csrf_token':record._get_outlook_csrf_token(),
                })
            }))

    defopen_microsoft_outlook_uri(self):
        """OpentheURLtoaccepttheOutlookpermission.

        Thisisdonewithanaction,sowecanforcetheuserthesavetheform.
        WeneedhimtosavetheformsothecurrentmailserverrecordexistinDB,and
        wecanincludetherecordIDintheURL.
        """
        self.ensure_one()

        ifnotself.env.user.has_group('base.group_system'):
            raiseAccessError(_('OnlytheadministratorcanlinkanOutlookmailserver.'))

        ifnotself.use_microsoft_outlook_serviceornotself.is_microsoft_outlook_configured:
            raiseUserError(_('PleaseconfigureyourOutlookcredentials.'))

        return{
            'type':'ir.actions.act_url',
            'url':self.microsoft_outlook_uri,
        }

    def_fetch_outlook_refresh_token(self,authorization_code):
        """Requesttherefreshtokenandtheinitialaccesstokenfromtheauthorizationcode.

        :return:
            refresh_token,access_token,access_token_expiration
        """
        response=self._fetch_outlook_token('authorization_code',code=authorization_code)
        return(
            response['refresh_token'],
            response['access_token'],
            int(time.time())+response['expires_in'],
        )

    def_fetch_outlook_access_token(self,refresh_token):
        """Refreshtheaccesstokenthankstotherefreshtoken.

        :return:
            access_token,access_token_expiration
        """
        response=self._fetch_outlook_token('refresh_token',refresh_token=refresh_token)
        return(
            response['refresh_token'],
            response['access_token'],
            int(time.time())+response['expires_in'],
        )

    def_fetch_outlook_token(self,grant_type,**values):
        """Genericmethodtorequestanaccesstokenorarefreshtoken.

        ReturntheJSONresponseoftheOutlookAPIandmanagetheerrorswhichcanoccur.

        :paramgrant_type:Dependstheactionwewanttodo(refresh_tokenorauthorization_code)
        :paramvalues:AdditionalparametersthatwillbegiventotheOutlookendpoint
        """
        Config=self.env['ir.config_parameter'].sudo()
        base_url=self.get_base_url()
        microsoft_outlook_client_id=Config.get_param('microsoft_outlook_client_id')
        microsoft_outlook_client_secret=Config.get_param('microsoft_outlook_client_secret')

        response=requests.post(
            url_join(self._get_microsoft_endpoint(),'token'),
            data={
                'client_id':microsoft_outlook_client_id,
                'client_secret':microsoft_outlook_client_secret,
                'scope':'offline_access%s'%self._OUTLOOK_SCOPE,
                'redirect_uri':url_join(base_url,'/microsoft_outlook/confirm'),
                'grant_type':grant_type,
                **values,
            },
            timeout=10,
        )

        ifnotresponse.ok:
            try:
                error_description=response.json()['error_description']
            exceptException:
                error_description=_('Unknownerror.')
            raiseUserError(_('Anerroroccurredwhenfetchingtheaccesstoken.%s')%error_description)

        returnresponse.json()

    def_generate_outlook_oauth2_string(self,login):
        """GenerateaOAuth2stringwhichcanbeusedforauthentication.

        :paramuser:EmailaddressoftheOutlookaccounttoauthenticate
        :return:TheSASLargumentfortheOAuth2mechanism.
        """
        self.ensure_one()
        now_timestamp=int(time.time())
        ifnotself.microsoft_outlook_access_token\
           ornotself.microsoft_outlook_access_token_expiration\
           orself.microsoft_outlook_access_token_expiration<now_timestamp:
            ifnotself.microsoft_outlook_refresh_token:
                raiseUserError(_('PleaseloginyourOutlookmailserverbeforeusingit.'))
            (
                self.microsoft_outlook_refresh_token,
                self.microsoft_outlook_access_token,
                self.microsoft_outlook_access_token_expiration,
            )=self._fetch_outlook_access_token(self.microsoft_outlook_refresh_token)
            _logger.info(
                'MicrosoftOutlook:fetchnewaccesstoken.Itexpiresin%iminutes',
                (self.microsoft_outlook_access_token_expiration-now_timestamp)//60)
        else:
            _logger.info(
                'MicrosoftOutlook:reuseexistingaccesstoken.Itexpiresin%iminutes',
                (self.microsoft_outlook_access_token_expiration-now_timestamp)//60)

        return'user=%s\1auth=Bearer%s\1\1'%(login,self.microsoft_outlook_access_token)

    def_get_outlook_csrf_token(self):
        """GenerateaCSRFtokenthatwillbeverifiedin`microsoft_outlook_callback`.

        Thiswillpreventamaliciouspersontomakeanadminuserdisconnectthemailservers.
        """
        self.ensure_one()
        _logger.info('MicrosoftOutlook:generateCSRFtokenfor%s#%i',self._name,self.id)
        returnhmac(
            env=self.env(su=True),
            scope='microsoft_outlook_oauth',
            message=(self._name,self.id),
        )

    @api.model
    def_get_microsoft_endpoint(self):
        returnself.env["ir.config_parameter"].sudo().get_param(
            'microsoft_outlook.endpoint',
            'https://login.microsoftonline.com/common/oauth2/v2.0/',
        )
