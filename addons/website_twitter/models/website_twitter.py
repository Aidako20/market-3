#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging

importrequests
fromflectraimportapi,fields,models

API_ENDPOINT='https://api.twitter.com'
API_VERSION='1.1'
REQUEST_TOKEN_URL='%s/oauth2/token'%API_ENDPOINT
REQUEST_FAVORITE_LIST_URL='%s/%s/favorites/list.json'%(API_ENDPOINT,API_VERSION)
URLOPEN_TIMEOUT=10

_logger=logging.getLogger(__name__)


classWebsiteTwitter(models.Model):
    _inherit='website'

    twitter_api_key=fields.Char(string='TwitterAPIkey',help='TwitterAPIKey',groups='base.group_system')
    twitter_api_secret=fields.Char(string='TwitterAPIsecret',help='TwitterAPISecret',groups='base.group_system')
    twitter_screen_name=fields.Char(string='Getfavoritesfromthisscreenname')

    @api.model
    def_request(self,website,url,params=None):
        """SendanauthenticatedrequesttotheTwitterAPI."""
        access_token=self._get_access_token(website)
        try:
            request=requests.get(url,params=params,headers={'Authorization':'Bearer%s'%access_token},timeout=URLOPEN_TIMEOUT)
            request.raise_for_status()
            returnrequest.json()
        exceptrequests.HTTPErrorase:
            _logger.debug("TwitterAPIrequestfailedwithcode:%r,msg:%r,content:%r",
                          e.response.status_code,e.response.reason,e.response.content)
            raise

    @api.model
    def_refresh_favorite_tweets(self):
        '''calledbycronjob'''
        website=self.env['website'].search([('twitter_api_key','!=',False),
                                          ('twitter_api_secret','!=',False),
                                          ('twitter_screen_name','!=',False)])
        _logger.debug("RefreshingtweetsforwebsiteIDs:%r",website.ids)
        website.fetch_favorite_tweets()

    deffetch_favorite_tweets(self):
        WebsiteTweets=self.env['website.twitter.tweet']
        tweet_ids=[]
        forwebsiteinself:
            ifnotall((website.sudo().twitter_api_key,website.sudo().twitter_api_secret,website.twitter_screen_name)):
                _logger.debug("Skipfetchingfavoritetweetsforunconfiguredwebsite%s",website)
                continue
            params={'screen_name':website.twitter_screen_name}
            last_tweet=WebsiteTweets.search([('website_id','=',website.id),
                                                     ('screen_name','=',website.twitter_screen_name)],
                                                     limit=1,order='tweet_iddesc')
            iflast_tweet:
                params['since_id']=int(last_tweet.tweet_id)
            _logger.debug("Fetchingfavoritetweetsusingparams%r",params)
            response=self._request(website,REQUEST_FAVORITE_LIST_URL,params=params)
            fortweet_dictinresponse:
                tweet_id=tweet_dict['id'] #unsigned64-bitsnowflakeID
                tweet_ids=WebsiteTweets.search([('tweet_id','=',tweet_id)]).ids
                ifnottweet_ids:
                    new_tweet=WebsiteTweets.create(
                            {
                              'website_id':website.id,
                              'tweet':json.dumps(tweet_dict),
                              'tweet_id':tweet_id, #storedinNUMERICPGfield
                              'screen_name':website.twitter_screen_name,
                            })
                    _logger.debug("Foundnewfavorite:%r,%r",tweet_id,tweet_dict)
                    tweet_ids.append(new_tweet.id)
        returntweet_ids

    def_get_access_token(self,website):
        """Obtainabearertoken."""
        r=requests.post(
            REQUEST_TOKEN_URL,
            data={'grant_type':'client_credentials',},
            auth=(website.sudo().twitter_api_key,website.sudo().twitter_api_secret),
            timeout=URLOPEN_TIMEOUT,
        )
        r.raise_for_status()
        data=r.json()
        access_token=data['access_token']
        returnaccess_token
