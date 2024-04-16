#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classPublisherWarrantyContract(models.AbstractModel):
    _inherit="publisher_warranty.contract"

    @api.model
    def_get_message(self):
        msg=super(PublisherWarrantyContract,self)._get_message()
        msg['website']=True
        returnmsg
