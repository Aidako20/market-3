#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResUsers(models.Model):
    _inherit='res.users'

    resource_ids=fields.One2many(
        'resource.resource','user_id','Resources')
    resource_calendar_id=fields.Many2one(
        'resource.calendar','DefaultWorkingHours',
        related='resource_ids.calendar_id',readonly=False)
