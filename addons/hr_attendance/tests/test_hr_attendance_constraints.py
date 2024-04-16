#-*-coding:utf-8-*-

importtime

fromflectra.tests.commonimportTransactionCase


classTestHrAttendance(TransactionCase):
    """Testsforattendancedaterangesvalidity"""

    defsetUp(self):
        super(TestHrAttendance,self).setUp()
        self.attendance=self.env['hr.attendance']
        self.test_employee=self.env['hr.employee'].create({'name':"Jacky"})
        #demodatacontainssetupforself.test_employee
        self.open_attendance=self.attendance.create({
            'employee_id':self.test_employee.id,
            'check_in':time.strftime('%Y-%m-1010:00'),
        })

    deftest_attendance_in_before_out(self):
        #Makesurecheck_outisbeforecheck_in
        withself.assertRaises(Exception):
            self.my_attend=self.attendance.create({
                'employee_id':self.test_employee.id,
                'check_in':time.strftime('%Y-%m-1012:00'),
                'check_out':time.strftime('%Y-%m-1011:00'),
            })

    deftest_attendance_no_check_out(self):
        #Makesurenosecondattandancewithoutcheck_outcanbecreated
        withself.assertRaises(Exception):
            self.attendance.create({
                'employee_id':self.test_employee.id,
                'check_in':time.strftime('%Y-%m-1011:00'),
            })

    #5nexttests:Makesurethatwhenattendancesoverlapanerrorisraised
    deftest_attendance_1(self):
        self.attendance.create({
            'employee_id':self.test_employee.id,
            'check_in':time.strftime('%Y-%m-1007:30'),
            'check_out':time.strftime('%Y-%m-1009:00'),
        })
        withself.assertRaises(Exception):
            self.attendance.create({
                'employee_id':self.test_employee.id,
                'check_in':time.strftime('%Y-%m-1008:30'),
                'check_out':time.strftime('%Y-%m-1009:30'),
            })

    deftest_new_attendances(self):
        #Makesureattendancemodificationraisesanerrorwhenitcausesanoverlap
        self.attendance.create({
            'employee_id':self.test_employee.id,
            'check_in':time.strftime('%Y-%m-1011:00'),
            'check_out':time.strftime('%Y-%m-1012:00'),
        })
        withself.assertRaises(Exception):
            self.open_attendance.write({
                'check_out':time.strftime('%Y-%m-1011:30'),
            })
