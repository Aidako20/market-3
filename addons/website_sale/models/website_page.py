#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels
fromflectra.httpimportrequest


classWabsitePage(models.AbstractModel):
    _inherit='website.page'

    def_get_cache_key(self,req):
        cart=request.website.sale_get_order()
        cache_key=(cartandcart.cart_quantityor0,)
        cache_key+=super()._get_cache_key(req)
        returncache_key
