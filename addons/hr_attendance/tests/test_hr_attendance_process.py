#-*-coding:utf-8-*-

importpytz
fromdatetimeimportdatetime
fromunittest.mockimportpatch

fromflectraimportfields
fromflectra.testsimportnew_test_user
fromflectra.tests.commonimportTransactionCase


classTestHrAttendance(TransactionCase):
    """Testforpresencevalidity"""

    defsetUp(self):
        super(TestHrAttendance,self).setUp()
        self.user=new_test_user(self.env,login='fru',groups='base.group_user,hr_attendance.group_hr_attendance_use_pin')
        self.user_no_pin=new_test_user(self.env,login='gru',groups='base.group_user')
        self.test_employee=self.env['hr.employee'].create({
            'name':"FrançoisRussie",
            'user_id':self.user.id,
            'pin':'1234',
        })
        self.employee_kiosk=self.env['hr.employee'].create({
            'name':"Machiavel",
            'pin':'5678',
        })

    deftest_employee_state(self):
        #Makesuretheattendanceoftheemployeewilldisplaycorrectly
        assertself.test_employee.attendance_state=='checked_out'
        self.test_employee._attendance_action_change()
        assertself.test_employee.attendance_state=='checked_in'
        self.test_employee._attendance_action_change()
        assertself.test_employee.attendance_state=='checked_out'

    deftest_checkin_self_without_pin(self):
        """Employeecancheckin/outwithoutpinwithhisownaccount"""
        employee=self.test_employee.with_user(self.user)
        employee.with_user(self.user).attendance_manual({},entered_pin=None)
        self.assertEqual(employee.attendance_state,'checked_in',"Heshouldbeabletocheckinwithoutpin")
        employee.attendance_manual({},entered_pin=None)
        self.assertEqual(employee.attendance_state,'checked_out',"Heshouldbeabletocheckoutwithoutpin")

    deftest_checkin_self_with_pin(self):
        """Employeecancheckin/outwithpinwithhisownaccount"""
        employee=self.test_employee.with_user(self.user)
        employee.attendance_manual({},entered_pin='1234')
        self.assertEqual(employee.attendance_state,'checked_in',"Heshouldbeabletocheckinwithhispin")
        employee.attendance_manual({},entered_pin='1234')
        self.assertEqual(employee.attendance_state,'checked_out',"Heshouldbeabletocheckoutwithhispin")

    deftest_checkin_self_wrong_pin(self):
        """Employeecannotcheckin/outwithwrongpinwithhisownaccount"""
        employee=self.test_employee.with_user(self.user)
        action=employee.attendance_manual({},entered_pin='9999')
        self.assertNotEqual(employee.attendance_state,'checked_in',"Heshouldnotbeabletocheckinwithawrongpin")
        self.assertTrue(action.get('warning'))

    deftest_checkin_kiosk_with_pin(self):
        """Employeecancheckin/outwithhispininkiosk"""
        employee=self.employee_kiosk.with_user(self.user)
        employee.attendance_manual({},entered_pin='5678')
        self.assertEqual(employee.attendance_state,'checked_in',"Heshouldbeabletocheckinwithhispin")
        employee.attendance_manual({},entered_pin='5678')
        self.assertEqual(employee.attendance_state,'checked_out',"Heshouldbeabletocheckoutwithhispin")

    deftest_checkin_kiosk_with_wrong_pin(self):
        """Employeecannotcheckin/outwithwrongpininkiosk"""
        employee=self.employee_kiosk.with_user(self.user)
        action=employee.attendance_manual({},entered_pin='8888')
        self.assertNotEqual(employee.attendance_state,'checked_in',"Heshouldnotbeabletocheckinwithawrongpin")
        self.assertTrue(action.get('warning'))

    deftest_checkin_kiosk_without_pin(self):
        """Employeecannotcheckin/outwithouthispininkiosk"""
        employee=self.employee_kiosk.with_user(self.user)
        action=employee.attendance_manual({},entered_pin=None)
        self.assertNotEqual(employee.attendance_state,'checked_in',"Heshouldnotbeabletocheckinwithnopin")
        self.assertTrue(action.get('warning'))

    deftest_checkin_kiosk_no_pin_mode(self):
        """Employeecannotcheckin/outwithoutpininkioskwhenuserhasnotgroup`use_pin`"""
        employee=self.employee_kiosk.with_user(self.user_no_pin)
        employee.attendance_manual({},entered_pin=None)
        self.assertEqual(employee.attendance_state,'checked_out',"Heshouldn'tbeabletocheckinwithout")

    deftest_hours_today(self):
        """Testdaystartiscorrectlycomputedaccordingtotheemployee'stimezone"""

        deftz_datetime(year,month,day,hour,minute):
            tz=pytz.timezone('Europe/Brussels')
            returntz.localize(datetime(year,month,day,hour,minute)).astimezone(pytz.utc).replace(tzinfo=None)

        employee=self.env['hr.employee'].create({'name':'Cunégonde','tz':'Europe/Brussels'})
        self.env['hr.attendance'].create({
            'employee_id':employee.id,
            'check_in':tz_datetime(2019,3,1,22,0), #shouldcountfrommidnightintheemployee'stimezone(=thepreviousdayinutc!)
            'check_out':tz_datetime(2019,3,2,2,0),
        })
        self.env['hr.attendance'].create({
            'employee_id':employee.id,
            'check_in':tz_datetime(2019,3,2,11,0),
        })

        #now=2019/3/214:00intheemployee'stimezone
        withpatch.object(fields.Datetime,'now',lambda:tz_datetime(2019,3,2,14,0).astimezone(pytz.utc).replace(tzinfo=None)):
            self.assertEqual(employee.hours_today,5,"Itshouldhavecounted5hours")
