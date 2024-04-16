#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

importrequests

fromflectraimportapi,fields,models,_,_lt
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)

TWITTER_EXCEPTION={
    304:_lt('Therewasnonewdatatoreturn.'),
    400:_lt('Therequestwasinvalidorcannotbeotherwiseserved.Requestswithoutauthenticationareconsideredinvalidandwillyieldthisresponse.'),
    401:_lt('Authenticationcredentialsweremissingorincorrect.Maybescreennametweetsareprotected.'),
    403:_lt('Therequestisunderstood,butithasbeenrefusedoraccessisnotallowed.PleasecheckyourTwitterAPIKeyandSecret.'),
    429:_lt('Requestcannotbeservedduetotheapplicationsratelimithavingbeenexhaustedfortheresource.'),
    500:_lt('Twitterseemsbroken.Pleaseretrylater.YoumayconsiderpostinganissueonTwitterforumstogethelp.'),
    502:_lt('Twitterisdownorbeingupgraded.'),
    503:_lt('TheTwitterserversareup,butoverloadedwithrequests.Tryagainlater.'),
    504:_lt('TheTwitterserversareup,buttherequestcouldnotbeservicedduetosomefailurewithinourstack.Tryagainlater.')
}


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    twitter_api_key=fields.Char(
        related='website_id.twitter_api_key',readonly=False,
        string='APIKey',
        help='TwitterAPIkeyyoucangetitfromhttps://apps.twitter.com/')
    twitter_api_secret=fields.Char(
        related='website_id.twitter_api_secret',readonly=False,
        string='APIsecret',
        help='TwitterAPIsecretyoucangetitfromhttps://apps.twitter.com/')
    twitter_screen_name=fields.Char(
        related='website_id.twitter_screen_name',readonly=False,
        string='FavoritesFrom',
        help='ScreenNameoftheTwitterAccountfromwhichyouwanttoloadfavorites.'
             'ItdoesnothavetomatchtheAPIKey/Secret.')
    twitter_server_uri=fields.Char(string='Twitterserveruri',readonly=True)

    def_get_twitter_exception_message(self,error_code):
        iferror_codeinTWITTER_EXCEPTION:
            returnTWITTER_EXCEPTION[error_code]
        else:
            return_('HTTPError:Somethingismisconfigured')

    def_check_twitter_authorization(self):
        try:
            self.website_id.fetch_favorite_tweets()

        exceptrequests.HTTPErrorase:
            _logger.info("%s-%s"%(e.response.status_code,e.response.reason),exc_info=True)
            raiseUserError("%s-%s"%(e.response.status_code,e.response.reason)+':'+self._get_twitter_exception_message(e.response.status_code))
        exceptIOError:
            _logger.info('Wefailedtoreachatwitterserver.',exc_info=True)
            raiseUserError(_('Internetconnectionrefused:Wefailedtoreachatwitterserver.'))
        exceptException:
            _logger.info('Pleasedouble-checkyourTwitterAPIKeyandSecret!',exc_info=True)
            raiseUserError(_('Twitterauthorizationerror!Pleasedouble-checkyourTwitterAPIKeyandSecret!'))

    @api.model
    defcreate(self,vals):
        TwitterConfig=super(ResConfigSettings,self).create(vals)
        ifvals.get('twitter_api_key')orvals.get('twitter_api_secret')orvals.get('twitter_screen_name'):
            TwitterConfig._check_twitter_authorization()
        returnTwitterConfig

    defwrite(self,vals):
        TwitterConfig=super(ResConfigSettings,self).write(vals)
        ifvals.get('twitter_api_key')orvals.get('twitter_api_secret')orvals.get('twitter_screen_name'):
            self._check_twitter_authorization()
        returnTwitterConfig

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        Params=self.env['ir.config_parameter'].sudo()
        res.update({
            'twitter_server_uri':'%s/'%Params.get_param('web.base.url',default='http://yourcompany.flectrahq.com'),
        })
        returnres
