#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_slides.controllers.mainimportWebsiteSlides
fromflectra.httpimportrequest


classWebsiteSaleSlides(WebsiteSlides):

    def_prepare_additional_channel_values(self,values,**kwargs):
        values=super(WebsiteSaleSlides,self)._prepare_additional_channel_values(values,**kwargs)
        channel=values['channel']
        ifchannel.enroll=='payment'andchannel.product_id:
            pricelist=request.website.get_current_pricelist()
            values['product_info']=channel.product_id.product_tmpl_id._get_combination_info(product_id=channel.product_id.id,pricelist=pricelist)
            values['product_info']['currency_id']=request.website.currency_id
        returnvalues
