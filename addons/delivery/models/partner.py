#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResPartner(models.Model):
    _inherit='res.partner'

    property_delivery_carrier_id=fields.Many2one('delivery.carrier',company_dependent=True,string="DeliveryMethod",help="Defaultdeliverymethodusedinsalesorders.")
