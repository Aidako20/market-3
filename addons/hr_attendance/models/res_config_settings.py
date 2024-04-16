#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_attendance_use_pin=fields.Boolean(string='EmployeePIN',
        implied_group="hr_attendance.group_hr_attendance_use_pin")
