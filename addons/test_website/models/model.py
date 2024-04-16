#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classTestModel(models.Model):
    """Addwebsiteoptioninserveractions."""

    _name='test.model'
    _inherit=['website.seo.metadata','website.published.mixin']
    _description='WebsiteModelTest'

    name=fields.Char(required=1)
