#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classResCompany(models.Model):
    _inherit="res.company"

    def_get_social_media_links(self):
        self.ensure_one()
        return{
            'social_facebook':self.social_facebook,
            'social_linkedin':self.social_linkedin,
            'social_twitter':self.social_twitter,
            'social_instagram':self.social_instagram
        }
