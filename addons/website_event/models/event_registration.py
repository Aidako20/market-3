#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classEventRegistration(models.Model):
    _name='event.registration'
    _inherit=['event.registration']

    visitor_id=fields.Many2one('website.visitor',string='Visitor',ondelete='setnull')

    def_get_website_registration_allowed_fields(self):
        return{'name','phone','email','mobile','event_id','partner_id','event_ticket_id'}
