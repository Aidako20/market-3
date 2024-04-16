#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,date,timedelta
fromdateutil.relativedeltaimportrelativedelta
frompytzimporttimezone,UTC

fromflectraimportfields
fromflectra.exceptionsimportValidationError
fromflectra.toolsimportmute_logger
fromflectra.tests.commonimportForm
fromflectra.testsimporttagged

fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon

@tagged('leave_requests')
classTestLeaveRequests(TestHrHolidaysCommon):

    def_check_holidays_status(self,holiday_status,ml,lt,rl,vrl):
            self.assertEqual(holiday_status.max_leaves,ml,
                             'hr_holidays:wrongtypedayscomputation')
            self.assertEqual(holiday_status.leaves_taken,lt,
                             'hr_holidays:wrongtypedayscomputation')
            self.assertEqual(holiday_status.remaining_leaves,rl,
                             'hr_holidays:wrongtypedayscomputation')
            self.assertEqual(holiday_status.virtual_remaining_leaves,vrl,
                             'hr_holidays:wrongtypedayscomputation')

    defsetUp(self):
        super(TestLeaveRequests,self).setUp()

        #Makesurewehavetherightstocreate,validateanddeletetheleaves,leavetypesandallocations
        LeaveType=self.env['hr.leave.type'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True)

        self.holidays_type_1=LeaveType.create({
            'name':'NotLimitedHR',
            'allocation_type':'no',
            'leave_validation_type':'hr',
            'validity_start':False,
        })
        self.holidays_type_2=LeaveType.create({
            'name':'Limited',
            'allocation_type':'fixed_allocation',
            'leave_validation_type':'hr',
            'validity_start':False,
        })
        self.holidays_type_3=LeaveType.create({
            'name':'TimeNotLimited',
            'allocation_type':'no',
            'leave_validation_type':'manager',
            'validity_start':fields.Datetime.from_string('2017-01-0100:00:00'),
            'validity_stop':fields.Datetime.from_string('2017-06-0100:00:00'),
        })

        self.set_employee_create_date(self.employee_emp_id,'2010-02-0300:00:00')
        self.set_employee_create_date(self.employee_hruser_id,'2010-02-0300:00:00')

    defset_employee_create_date(self,id,newdate):
        """Thismethodisahackinordertobeabletodefine/redefinethecreate_date
            oftheemployees.
            ThisisdoneinSQLbecauseORMdoesnotallowtowriteontothecreate_datefield.
        """
        self.env.cr.execute("""
                       UPDATE
                       hr_employee
                       SETcreate_date='%s'
                       WHEREid=%s
                       """%(newdate,id))

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_overlapping_requests(self):
        """ Employeecannotcreateanewleaverequestatthesametime,avoidinterlapping """
        self.env['hr.leave'].with_user(self.user_employee_id).create({
            'name':'Hol11',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_type_1.id,
            'date_from':(datetime.today()-relativedelta(days=1)),
            'date_to':datetime.today(),
            'number_of_days':1,
        })

        withself.assertRaises(ValidationError):
            self.env['hr.leave'].with_user(self.user_employee_id).create({
                'name':'Hol21',
                'employee_id':self.employee_emp_id,
                'holiday_status_id':self.holidays_type_1.id,
                'date_from':(datetime.today()-relativedelta(days=1)),
                'date_to':datetime.today(),
                'number_of_days':1,
            })

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_limited_type_no_days(self):
        """ Employeecreatesaleaverequestinalimitedcategorybuthasnotenoughdaysleft """

        withself.assertRaises(ValidationError):
            self.env['hr.leave'].with_user(self.user_employee_id).create({
                'name':'Hol22',
                'employee_id':self.employee_emp_id,
                'holiday_status_id':self.holidays_type_2.id,
                'date_from':(datetime.today()+relativedelta(days=1)).strftime('%Y-%m-%d%H:%M'),
                'date_to':(datetime.today()+relativedelta(days=2)),
                'number_of_days':1,
            })

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_limited_type_days_left(self):
        """ Employeecreatesaleaverequestinalimitedcategoryandhasenoughdaysleft """
        aloc1_user_group=self.env['hr.leave.allocation'].with_user(self.user_hruser_id).create({
            'name':'Daysforlimitedcategory',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_type_2.id,
            'number_of_days':2,
        })
        aloc1_user_group.action_approve()

        holiday_status=self.holidays_type_2.with_user(self.user_employee_id)
        self._check_holidays_status(holiday_status,2.0,0.0,2.0,2.0)

        hol=self.env['hr.leave'].with_user(self.user_employee_id).create({
            'name':'Hol11',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_type_2.id,
            'date_from':(datetime.today()-relativedelta(days=2)),
            'date_to':datetime.today(),
            'number_of_days':2,
        })

        holiday_status.invalidate_cache()
        self._check_holidays_status(holiday_status,2.0,0.0,2.0,0.0)

        hol.with_user(self.user_hrmanager_id).action_approve()

        holiday_status.invalidate_cache(['max_leaves'])
        self._check_holidays_status(holiday_status,2.0,2.0,0.0,0.0)

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_accrual_validity_time_valid(self):
        """ Employeeaskleaveduringavalidvaliditytime"""
        self.env['hr.leave'].with_user(self.user_employee_id).create({
            'name':'Validtimeperiod',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_type_3.id,
            'date_from':fields.Datetime.from_string('2017-03-0306:00:00'),
            'date_to':fields.Datetime.from_string('2017-03-1119:00:00'),
            'number_of_days':1,
        })

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_accrual_validity_time_not_valid(self):
        """ Employeeaskleavduringanotvalidvaliditytime"""
        withself.assertRaises(ValidationError):
            self.env['hr.leave'].with_user(self.user_employee_id).create({
                'name':'SickTimeOff',
                'employee_id':self.employee_emp_id,
                'holiday_status_id':self.holidays_type_3.id,
                'date_from':fields.Datetime.from_string('2017-07-0306:00:00'),
                'date_to':fields.Datetime.from_string('2017-07-1119:00:00'),
                'number_of_days':1,
            })

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_department_leave(self):
        """Createadepartmentleave"""
        self.employee_hrmanager.write({'department_id':self.hr_dept.id})
        self.assertFalse(self.env['hr.leave'].search([('employee_id','in',self.hr_dept.member_ids.ids)]))
        leave_form=Form(self.env['hr.leave'].with_user(self.user_hrmanager),view='hr_holidays.hr_leave_view_form_manager')
        leave_form.holiday_type='department'
        leave_form.department_id=self.hr_dept
        leave_form.holiday_status_id=self.holidays_type_1
        leave_form.request_date_from=date(2019,5,6)
        leave_form.request_date_to=date(2019,5,6)
        leave=leave_form.save()
        leave.action_approve()
        member_ids=self.hr_dept.member_ids.ids
        self.assertEqual(self.env['hr.leave'].search_count([('employee_id','in',member_ids)]),len(member_ids),"Leaveshouldbecreatedformembersofdepartment")

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_allocation_request(self):
        """Createanallocationrequest"""
        #employeeshouldbesettocurrentuser
        allocation_form=Form(self.env['hr.leave.allocation'].with_user(self.user_employee))
        allocation_form.name='NewAllocationRequest'
        allocation_form.holiday_status_id=self.holidays_type_2
        allocation=allocation_form.save()

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_employee_is_absent(self):
        """Onlytheconcernedemployeeshouldbeconsideredabsent"""
        user_employee_leave=self.env['hr.leave'].with_user(self.user_employee_id).create({
            'name':'Hol11',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_type_1.id,
            'date_from':(fields.Datetime.now()-relativedelta(days=1)),
            'date_to':fields.Datetime.now()+relativedelta(days=1),
            'number_of_days':2,
        })
        (self.employee_emp|self.employee_hrmanager).mapped('is_absent') #computeinbatch
        self.assertFalse(self.employee_emp.is_absent,"Heshouldnotbeconsideredabsent")
        self.assertFalse(self.employee_hrmanager.is_absent,"Heshouldnotbeconsideredabsent")

        user_employee_leave.sudo().write({
            'state':'validate',
        })
        (self.employee_emp|self.employee_hrmanager)._compute_leave_status()
        self.assertTrue(self.employee_emp.is_absent,"Heshouldbeconsideredabsent")
        self.assertFalse(self.employee_hrmanager.is_absent,"Heshouldnotbeconsideredabsent")

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_timezone_employee_leave_request(self):
        """Createaleaverequestforanemployeeinanothertimezone"""
        self.employee_emp.tz='NZ' #GMT+12
        leave=self.env['hr.leave'].new({
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.holidays_type_1.id,
            'request_unit_hours':True,
            'request_date_from':date(2019,5,6),
            'request_date_to':date(2019,5,6),
            'request_hour_from':'8', #8:00AMintheemployee'stimezone
            'request_hour_to':'17', #5:00PMintheemployee'stimezone
        })
        self.assertEqual(leave.date_from,datetime(2019,5,5,20,0,0),"ItshouldhavebeenlocalizedbeforesavinginUTC")
        self.assertEqual(leave.date_to,datetime(2019,5,6,5,0,0),"ItshouldhavebeenlocalizedbeforesavinginUTC")

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_timezone_company_leave_request(self):
        """Createaleaverequestforacompanyinanothertimezone"""
        company=self.env['res.company'].create({'name':"Hergé"})
        company.resource_calendar_id.tz='NZ' #GMT+12
        leave=self.env['hr.leave'].new({
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.holidays_type_1.id,
            'request_unit_hours':True,
            'holiday_type':'company',
            'mode_company_id':company.id,
            'request_date_from':date(2019,5,6),
            'request_date_to':date(2019,5,6),
            'request_hour_from':'8', #8:00AMinthecompany'stimezone
            'request_hour_to':'17', #5:00PMinthecompany'stimezone
        })
        self.assertEqual(leave.date_from,datetime(2019,5,5,20,0,0),"ItshouldhavebeenlocalizedbeforesavinginUTC")
        self.assertEqual(leave.date_to,datetime(2019,5,6,5,0,0),"ItshouldhavebeenlocalizedbeforesavinginUTC")

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_timezone_company_validated(self):
        """Createaleaverequestforacompanyinanothertimezoneandvalidateit"""
        self.env.user.tz='NZ'#GMT+12
        company=self.env['res.company'].create({'name':"Hergé"})
        employee=self.env['hr.employee'].create({'name':"Remi",'company_id':company.id})
        leave_form=Form(self.env['hr.leave'],view='hr_holidays.hr_leave_view_form_manager')
        leave_form.holiday_type='company'
        leave_form.mode_company_id=company
        leave_form.holiday_status_id=self.holidays_type_1
        leave_form.request_date_from=date(2019,5,6)
        leave_form.request_date_to=date(2019,5,6)
        leave=leave_form.save()
        leave.state='confirm'
        leave.action_validate()
        employee_leave=self.env['hr.leave'].search([('employee_id','=',employee.id)])
        self.assertEqual(
            employee_leave.request_date_from,date(2019,5,6),
            "Timezoneshouldbekeptbetweencompanyandemployeeleave"
        )

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_timezone_department_leave_request(self):
        """Createaleaverequestforadepartmentinanothertimezone"""
        company=self.env['res.company'].create({'name':"Hergé"})
        company.resource_calendar_id.tz='NZ' #GMT+12
        department=self.env['hr.department'].create({'name':"Museum",'company_id':company.id})
        leave=self.env['hr.leave'].new({
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.holidays_type_1.id,
            'request_unit_hours':True,
            'holiday_type':'department',
            'department_id':department.id,
            'request_date_from':date(2019,5,6),
            'request_date_to':date(2019,5,6),
            'request_hour_from':'8', #8:00AMinthedepartment'stimezone
            'request_hour_to':'17', #5:00PMinthedepartment'stimezone
        })
        self.assertEqual(leave.date_from,datetime(2019,5,5,20,0,0),"ItshouldhavebeenlocalizedbeforesavinginUTC")
        self.assertEqual(leave.date_to,datetime(2019,5,6,5,0,0),"ItshouldhavebeenlocalizedbeforesavinginUTC")

    deftest_number_of_hours_display(self):
        #Testthatthefieldnumber_of_hours_dispaydoesn'tchange
        #aftertimeoffvalidation,asittakestheattendances
        #minustheresourceleavestocomputethatfield.
        calendar=self.env['resource.calendar'].create({
            'name':'MondayMorningElseFullTime38h/week',
            'hours_per_day':7.6,
            'attendance_ids':[
                (0,0,{'name':'MondayMorning','dayofweek':'0','hour_from':8.5,'hour_to':12.5,'day_period':'morning'}),
                (0,0,{'name':'TuesdayMorning','dayofweek':'1','hour_from':8.5,'hour_to':12.5,'day_period':'morning'}),
                (0,0,{'name':'TuesdayAfternoon','dayofweek':'1','hour_from':13,'hour_to':17.5,'day_period':'afternoon'}),
                (0,0,{'name':'WednesdayMorning','dayofweek':'2','hour_from':8.5,'hour_to':12.5,'day_period':'morning'}),
                (0,0,{'name':'WednesdayAfternoon','dayofweek':'2','hour_from':13,'hour_to':17.5,'day_period':'afternoon'}),
                (0,0,{'name':'ThursdayMorning','dayofweek':'3','hour_from':8.5,'hour_to':12.5,'day_period':'morning'}),
                (0,0,{'name':'ThursdayAfternoon','dayofweek':'3','hour_from':13,'hour_to':17.5,'day_period':'afternoon'}),
                (0,0,{'name':'FridayMorning','dayofweek':'4','hour_from':8.5,'hour_to':12.5,'day_period':'morning'}),
                (0,0,{'name':'FridayAfternoon','dayofweek':'4','hour_from':13,'hour_to':17.5,'day_period':'afternoon'})
            ],
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar
        self.env.user.company_id.resource_calendar_id=calendar
        leave_type=self.env['hr.leave.type'].create({
            'name':'PaidTimeOff',
            'request_unit':'hour',
            'leave_validation_type':'both',
        })
        allocation=self.env['hr.leave.allocation'].create({
            'name':'20daysallocation',
            'holiday_status_id':leave_type.id,
            'number_of_days':20,
            'employee_id':employee.id,
        })
        allocation.action_approve()

        leave1=self.env['hr.leave'].create({
            'name':'Holiday1week',
            'employee_id':employee.id,
            'holiday_status_id':leave_type.id,
            'date_from':fields.Datetime.from_string('2019-12-2306:00:00'),
            'date_to':fields.Datetime.from_string('2019-12-2720:00:00'),
            'number_of_days':5,
        })

        self.assertEqual(leave1.number_of_hours_display,38)
        leave1.action_approve()
        self.assertEqual(leave1.number_of_hours_display,38)
        leave1.action_validate()
        self.assertEqual(leave1.number_of_hours_display,38)

        leave2=self.env['hr.leave'].create({
            'name':'Holiday1Day',
            'employee_id':employee.id,
            'holiday_status_id':leave_type.id,
            'date_from':fields.Datetime.from_string('2019-12-3006:00:00'),
            'date_to':fields.Datetime.from_string('2019-12-3013:00:00'),
            'number_of_days':1,
        })

        self.assertEqual(leave2.number_of_hours_display,4)
        leave2.action_approve()
        self.assertEqual(leave2.number_of_hours_display,4)
        leave2.action_validate()
        self.assertEqual(leave2.number_of_hours_display,4)

    deftest_number_of_hours_display_global_leave(self):
        #Checkthatthefieldnumber_of_hours_display
        #takesthegloballeavesintoaccount,even
        #aftervalidation
        calendar=self.env['resource.calendar'].create({
            'name':'Classic40h/week',
            'hours_per_day':8.0,
            'attendance_ids':[
                (0,0,{'name':'MondayMorning','dayofweek':'0','hour_from':8,'hour_to':12,'day_period':'morning'}),
                (0,0,{'name':'MondayAfternoon','dayofweek':'0','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                (0,0,{'name':'TuesdayMorning','dayofweek':'1','hour_from':8,'hour_to':12,'day_period':'morning'}),
                (0,0,{'name':'TuesdayAfternoon','dayofweek':'1','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                (0,0,{'name':'WednesdayMorning','dayofweek':'2','hour_from':8,'hour_to':12,'day_period':'morning'}),
                (0,0,{'name':'WednesdayAfternoon','dayofweek':'2','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                (0,0,{'name':'ThursdayMorning','dayofweek':'3','hour_from':8,'hour_to':12,'day_period':'morning'}),
                (0,0,{'name':'ThursdayAfternoon','dayofweek':'3','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
                (0,0,{'name':'FridayMorning','dayofweek':'4','hour_from':8,'hour_to':12,'day_period':'morning'}),
                (0,0,{'name':'FridayAfternoon','dayofweek':'4','hour_from':13,'hour_to':17,'day_period':'afternoon'})
            ],
            'global_leave_ids':[(0,0,{
                'name':'ChristmasLeave',
                'date_from':fields.Datetime.from_string('2019-12-2500:00:00'),
                'date_to':fields.Datetime.from_string('2019-12-2623:59:59'),
                'resource_id':False,
                'time_type':'leave',
            })]
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar
        self.env.user.company_id.resource_calendar_id=calendar
        leave_type=self.env['hr.leave.type'].create({
            'name':'Sick',
            'request_unit':'hour',
            'leave_validation_type':'both',
            'allocation_type':'no',
        })
        leave1=self.env['hr.leave'].create({
            'name':'Sick1weekduringchristmassnif',
            'employee_id':employee.id,
            'holiday_status_id':leave_type.id,
            'date_from':fields.Datetime.from_string('2019-12-2306:00:00'),
            'date_to':fields.Datetime.from_string('2019-12-2720:00:00'),
            'number_of_days':5,
        })
        self.assertEqual(leave1.number_of_hours_display,24)
        leave1.action_approve()
        self.assertEqual(leave1.number_of_hours_display,24)
        leave1.action_validate()
        self.assertEqual(leave1.number_of_hours_display,24)

    def_test_leave_with_tz(self,tz,local_date_from,local_date_to,number_of_days):
        self.user_employee.tz=tz
        tz=timezone(tz)

        #Mimicwhatisdonebythecalendarwidgetwhenclickingonaday.It
        #willtakethelocaldatetimefrom7:00to19:00andthenconvertit
        #toUTCbeforesendingit.ValueshereareforPST(UTC-8)and
        #representaleaveon2019/1/1from7:00to19:00localtime.
        values={
            'date_from':tz.localize(local_date_from).astimezone(UTC).replace(tzinfo=None),
            'date_to':tz.localize(local_date_to).astimezone(UTC).replace(tzinfo=None), #notethatthiscanbethenextdayinUTC
        }
        values.update(self.env['hr.leave'].with_user(self.user_employee_id)._default_get_request_parameters(values))

        #Datesshouldbelocaltotheuser
        self.assertEqual(values['request_date_from'],local_date_from.date())
        self.assertEqual(values['request_date_to'],local_date_to.date())

        values.update({
            'name':'Test',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_type_1.id,
        })
        leave=self.env['hr.leave'].with_user(self.user_employee_id).new(values)
        self.assertEqual(leave.number_of_days,number_of_days)

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_defaults_with_timezones(self):
        """Makesurethatleavesstartwithcorrectdefaultsfornon-UTCtimezones"""
        timezones_to_test=('UTC','Pacific/Midway','US/Pacific','Asia/Taipei','Pacific/Kiritimati') #UTC,UTC-11,UTC-8,UTC+8,UTC+14

        #    January2020
        #SuMoTuWeThFrSa
        #          1 2 3 4
        # 5 6 7 8 91011
        #12131415161718
        #19202122232425
        #262728293031
        local_date_from=datetime(2019,1,1,7,0,0)
        local_date_to=datetime(2019,1,1,19,0,0)
        fortzintimezones_to_test:
            self._test_leave_with_tz(tz,local_date_from,local_date_to,1)

        #We,Th,Fr,Mo,Tu,We=>6days
        local_date_from=datetime(2019,1,1,7,0,0)
        local_date_to=datetime(2019,1,8,19,0,0)
        fortzintimezones_to_test:
            self._test_leave_with_tz(tz,local_date_from,local_date_to,6)

    deftest_leave_with_public_holiday_other_company(self):
        other_company=self.env['res.company'].create({
            'name':'TestCompany',
        })
        #Createapublicholidayforthesecondcompany
        p_leave=self.env['resource.calendar.leaves'].create({
            'date_from':datetime(2022,3,11),
            'date_to':datetime(2022,3,11,23,59,59),
        })
        p_leave.company_id=other_company

        leave=self.env['hr.leave'].with_user(self.user_employee_id).create({
            'name':'HolidayRequest',
            'holiday_type':'employee',
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.holidays_type_1.id,
            'date_from':datetime(2022,3,11),
            'date_to':datetime(2022,3,11,23,59,59),
        })
        self.assertEqual(leave.number_of_days,1)

    deftest_current_leave_status(self):
        types=('no_validation','manager','hr','both')
        employee=self.employee_emp

        defrun_validation_flow(leave_validation_type):
            LeaveType=self.env['hr.leave.type'].with_user(self.user_hrmanager_id)
            leave_type=LeaveType.with_context(tracking_disable=True).create({
                'name':leave_validation_type.capitalize(),
                'leave_validation_type':leave_validation_type,
                'allocation_type':'no',
            })
            current_leave=self.env['hr.leave'].with_user(self.user_employee_id).create({
                'name':'HolidayRequest',
                'holiday_type':'employee',
                'employee_id':employee.id,
                'holiday_status_id':leave_type.id,
                'date_from':fields.Date.today(),
                'date_to':fields.Date.today()+timedelta(days=2),
                'number_of_days':2,
            })

            ifleave_validation_typein('manager','both'):
                self.assertFalse(employee.is_absent)
                self.assertFalse(employee.current_leave_id)
                self.assertEqual(employee.filtered_domain([('is_absent','=',False)]),employee)
                self.assertFalse(employee.filtered_domain([('is_absent','=',True)]))
                current_leave.with_user(self.user_hruser_id).action_approve()

            ifleave_validation_typein('hr','both'):
                self.assertFalse(employee.is_absent)
                self.assertFalse(employee.current_leave_id)
                self.assertEqual(employee.filtered_domain([('is_absent','=',False)]),employee)
                self.assertFalse(employee.filtered_domain([('is_absent','=',True)]))
                current_leave.with_user(self.user_hrmanager_id).action_validate()

            self.assertTrue(employee.is_absent)
            self.assertEqual(employee.current_leave_id,current_leave.holiday_status_id)
            self.assertFalse(employee.filtered_domain([('is_absent','=',False)]))
            self.assertEqual(employee.filtered_domain([('is_absent','=',True)]),employee)

            raiseRuntimeError()

        forleave_validation_typeintypes:
            withself.assertRaises(RuntimeError),self.env.cr.savepoint():
                run_validation_flow(leave_validation_type)
