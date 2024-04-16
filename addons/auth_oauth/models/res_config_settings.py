#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,fields,models

_logger=logging.getLogger(__name__)


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    @api.model
    defget_uri(self):
        return"%s/auth_oauth/signin"%(self.env['ir.config_parameter'].get_param('web.base.url'))

    auth_oauth_google_enabled=fields.Boolean(string='AllowuserstosigninwithGoogle')
    auth_oauth_google_client_id=fields.Char(string='ClientID')
    server_uri_google=fields.Char(string='Serveruri')

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        google_provider=self.env.ref('auth_oauth.provider_google',False)
        google_providerandres.update(
            auth_oauth_google_enabled=google_provider.enabled,
            auth_oauth_google_client_id=google_provider.client_id,
            server_uri_google=self.get_uri(),
        )
        returnres

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        google_provider=self.env.ref('auth_oauth.provider_google',False)
        google_providerandgoogle_provider.write({
            'enabled':self.auth_oauth_google_enabled,
            'client_id':self.auth_oauth_google_client_id,
        })
