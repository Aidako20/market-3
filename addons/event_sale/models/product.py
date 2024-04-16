#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classProductTemplate(models.Model):
    _inherit='product.template'

    event_ok=fields.Boolean(string='IsanEventTicket',help="Ifcheckedthisproductautomatically"
      "createsaneventregistrationatthesalesorderconfirmation.")

    @api.onchange('event_ok')
    def_onchange_event_ok(self):
        ifself.event_ok:
            self.type='service'


classProduct(models.Model):
    _inherit='product.product'

    event_ticket_ids=fields.One2many('event.event.ticket','product_id',string='EventTickets')

    @api.onchange('event_ok')
    def_onchange_event_ok(self):
        """Redirection,inheritancemechanismhidesthemethodonthemodel"""
        ifself.event_ok:
            self.type='service'
