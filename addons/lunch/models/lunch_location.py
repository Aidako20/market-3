#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classLunchLocation(models.Model):
    _name='lunch.location'
    _description='LunchLocations'

    name=fields.Char('LocationName',required=True)
    address=fields.Text('Address')
    company_id=fields.Many2one('res.company',default=lambdaself:self.env.company)
