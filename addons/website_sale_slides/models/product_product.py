#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classProduct(models.Model):
    _inherit="product.product"

    channel_ids=fields.One2many('slide.channel','product_id',string='Courses')
