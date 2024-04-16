#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classContacts(models.Model):
    _name='calendar.contacts'
    _description='CalendarContacts'

    user_id=fields.Many2one('res.users','Me',required=True,default=lambdaself:self.env.user)
    partner_id=fields.Many2one('res.partner','Employee',required=True)
    active=fields.Boolean('Active',default=True)

    _sql_constraints=[
        ('user_id_partner_id_unique','UNIQUE(user_id,partner_id)','Ausercannothavethesamecontacttwice.')
    ]

    @api.model
    defunlink_from_partner_id(self,partner_id):
        returnself.search([('partner_id','=',partner_id)]).unlink()
