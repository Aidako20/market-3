#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAttachment(models.Model):

    _inherit=['ir.attachment']

    product_downloadable=fields.Boolean("Downloadablefromproductportal",default=False)
