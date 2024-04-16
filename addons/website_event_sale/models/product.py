#-*-coding:utf-8-*-

fromflectraimportfields,models


#definedforaccessrules
classProduct(models.Model):
    _inherit='product.product'

    event_ticket_ids=fields.One2many('event.event.ticket','product_id',string='EventTickets')

    def_is_add_to_cart_allowed(self):
        #Allowaddingeventticketstothecartregardlessofproduct'srules
        self.ensure_one()
        res=super()._is_add_to_cart_allowed()
        returnresorany(event.website_publishedforeventinself.event_ticket_ids.event_id)
