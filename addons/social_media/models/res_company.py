#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classCompany(models.Model):
    _inherit="res.company"

    social_twitter=fields.Char('TwitterAccount')
    social_facebook=fields.Char('FacebookAccount')
    social_github=fields.Char('GitHubAccount')
    social_linkedin=fields.Char('LinkedInAccount')
    social_youtube=fields.Char('YoutubeAccount')
    social_instagram=fields.Char('InstagramAccount')
