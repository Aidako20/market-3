#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classWebsiteTwitterTweet(models.Model):
    _name='website.twitter.tweet'
    _description='WebsiteTwitter'

    website_id=fields.Many2one('website',string='Website',ondelete='cascade')
    screen_name=fields.Char(string='ScreenName')
    tweet=fields.Text(string='Tweets')

    #TwitterIDsare64-bitunsignedints,soweneedtostorethemin
    #unlimitedprecisionNUMERICcolumns,whichcanbedonewitha
    #floatfield.Useddigits=(0,0)toindicateunlimited.
    #UsingVARCHARwouldworktoobutwouldhavesortingproblems.
    tweet_id=fields.Float(string='TweetID',digits=(0,0)) #Twitter
