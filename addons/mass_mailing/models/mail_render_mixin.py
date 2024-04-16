#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classMailRenderMixin(models.AbstractModel):
    _inherit="mail.render.mixin"

    @api.model
    def_render_template_postprocess(self,rendered):
        #superwilltransformrelativeurltoabsolute
        rendered=super(MailRenderMixin,self)._render_template_postprocess(rendered)

        #applyshortenerafter
        ifself.env.context.get('post_convert_links'):
            forres_id,htmlinrendered.items():
                rendered[res_id]=self._shorten_links(
                    html,
                    self.env.context['post_convert_links'],
                    blacklist=['/unsubscribe_from_list','/view']
                )
        returnrendered
