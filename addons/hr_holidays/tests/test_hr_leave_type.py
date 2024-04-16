#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectra.exceptionsimportAccessError

fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon


classTestHrLeaveType(TestHrHolidaysCommon):

    deftest_time_type(self):
        leave_type=self.env['hr.leave.type'].create({
            'name':'PaidTimeOff',
            'time_type':'leave',
            'allocation_type':'no',
            'validity_start':False,
        })

        leave_1=self.env['hr.leave'].create({
            'name':'DoctorAppointment',
            'employee_id':self.employee_hruser_id,
            'holiday_status_id':leave_type.id,
            'date_from':(datetime.today()-relativedelta(days=1)),
            'date_to':datetime.today(),
            'number_of_days':1,
        })
        leave_1.action_approve()

        self.assertEqual(
            self.env['resource.calendar.leaves'].search([('holiday_id','=',leave_1.id)]).time_type,
            'leave'
        )

    deftest_type_creation_right(self):
        #HrUsercreatessomeholidaystatuses->crashbecauseonlyHrManagersshoulddothis
        withself.assertRaises(AccessError):
            self.env['hr.leave.type'].with_user(self.user_hruser_id).create({
                'name':'UserCheats',
                'allocation_type':'no',
            })
