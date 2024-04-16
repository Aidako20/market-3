#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classResCompany(models.Model):
    _inherit="res.company"

    def_get_social_media_links(self):
        social_media_links=super()._get_social_media_links()
        website_id=self.env['website'].get_current_website()
        social_media_links.update({
            'social_facebook':website_id.social_facebookorsocial_media_links.get('social_facebook'),
            'social_linkedin':website_id.social_linkedinorsocial_media_links.get('social_linkedin'),
            'social_twitter':website_id.social_twitterorsocial_media_links.get('social_twitter'),
            'social_instagram':website_id.social_instagramorsocial_media_links.get('social_instagram')
        })
        returnsocial_media_links
