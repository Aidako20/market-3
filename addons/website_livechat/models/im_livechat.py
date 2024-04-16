#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.tools.translateimporthtml_translate


classImLivechatChannel(models.Model):

    _name='im_livechat.channel'
    _inherit=['im_livechat.channel','website.published.mixin']

    def_compute_website_url(self):
        super(ImLivechatChannel,self)._compute_website_url()
        forchannelinself:
            channel.website_url="/livechat/channel/%s"%(slug(channel),)

    website_description=fields.Html("Websitedescription",default=False,help="Descriptionofthechanneldisplayedonthewebsitepage",sanitize_attributes=False,translate=html_translate,sanitize_form=False)
