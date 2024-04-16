#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classResourceCalendarAttendance(models.Model):
    _inherit='resource.calendar.attendance'

    def_default_work_entry_type_id(self):
        returnself.env.ref('hr_work_entry.work_entry_type_attendance',raise_if_not_found=False)

    work_entry_type_id=fields.Many2one('hr.work.entry.type','WorkEntryType',default=_default_work_entry_type_id)

    def_copy_attendance_vals(self):
        res=super()._copy_attendance_vals()
        res['work_entry_type_id']=self.work_entry_type_id.id
        returnres


classResourceCalendarLeave(models.Model):
    _inherit='resource.calendar.leaves'

    work_entry_type_id=fields.Many2one('hr.work.entry.type','WorkEntryType')

    def_copy_leave_vals(self):
        res=super()._copy_leave_vals()
        res['work_entry_type_id']=self.work_entry_type_id.id
        returnres
