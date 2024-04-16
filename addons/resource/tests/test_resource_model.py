#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResourceTest(models.Model):
    _description='TestResourceModel'
    _name='resource.test'
    _inherit=['resource.mixin']

    name=fields.Char()
