#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.addons.http_routing.models.ir_httpimporturl_for


classWebsite(models.Model):
    _inherit='website'

    @api.model
    defget_default_forum_count(self):
        self.forums_count=self.env['forum.forum'].search_count(self.website_domain())

    forums_count=fields.Integer(readonly=True,default=get_default_forum_count)

    defget_suggested_controllers(self):
        suggested_controllers=super(Website,self).get_suggested_controllers()
        suggested_controllers.append((_('Forum'),url_for('/forum'),'website_forum'))
        returnsuggested_controllers
