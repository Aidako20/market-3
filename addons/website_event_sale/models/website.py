#-*-coding:utf-8-*-

fromflectraimportmodels


classWebsite(models.Model):
    _inherit='website'

    defsale_product_domain(self):
        #removeproducteventfromthewebsitecontentgridandlistview(notremovedindetailview)
        return['&']+super(Website,self).sale_product_domain()+[('event_ok','=',False)]
