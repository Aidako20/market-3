#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classEventConfigurator(models.TransientModel):
    _name='event.event.configurator'
    _description='EventConfigurator'

    product_id=fields.Many2one('product.product',string="Product",readonly=True)
    event_id=fields.Many2one('event.event',string="Event")
    event_ticket_id=fields.Many2one('event.event.ticket',string="EventTicket")
