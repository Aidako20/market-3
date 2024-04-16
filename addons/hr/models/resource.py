#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResourceResource(models.Model):
    _inherit="resource.resource"

    user_id=fields.Many2one(copy=False)
