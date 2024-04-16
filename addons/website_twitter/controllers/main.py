#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
fromflectraimport_
fromflectraimporthttp
fromflectra.httpimportrequest


classTwitter(http.Controller):
    @http.route(['/website_twitter/reload'],type='json',auth="user",website=True)
    deftwitter_reload(self):
        returnrequest.website.fetch_favorite_tweets()

    @http.route(['/website_twitter/get_favorites'],type='json',auth="public",website=True)
    defget_tweets(self,limit=20):
        key=request.website.sudo().twitter_api_key
        secret=request.website.sudo().twitter_api_secret
        screen_name=request.website.twitter_screen_name
        debug=request.env['res.users'].has_group('website.group_website_publisher')
        ifnotkeyornotsecret:
            ifdebug:
                return{"error":_("PleasesettheTwitterAPIKeyandSecretintheWebsiteSettings.")}
            return[]
        ifnotscreen_name:
            ifdebug:
                return{"error":_("PleasesetaTwitterscreennametoloadfavoritesfrom,"
                                   "intheWebsiteSettings(itdoesnothavetobeyours)")}
            return[]
        TwitterTweets=request.env['website.twitter.tweet']
        tweets=TwitterTweets.search(
                [('website_id','=',request.website.id),
                 ('screen_name','=',screen_name)],
                limit=int(limit),order="tweet_iddesc")
        iflen(tweets)<12:
            ifdebug:
                return{"error":_("Twitteruser@%(username)shaslessthan12favoritetweets."
                                   "Pleaseaddmoreorchooseadifferentscreenname.")%\
                                      {'username':screen_name}}
            else:
                return[]
        returntweets.mapped(lambdat:json.loads(t.tweet))
