#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCalendarLeaves(models.Model):
    _inherit="resource.calendar.leaves"

    holiday_id=fields.Many2one("hr.leave",string='LeaveRequest')
