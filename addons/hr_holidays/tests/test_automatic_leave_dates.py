#-*-coding:utf-8-*-
fromdatetimeimportdate,datetime

fromflectra.tests.commonimportForm

fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon
fromflectra.exceptionsimportValidationError


classTestAutomaticLeaveDates(TestHrHolidaysCommon):
    defsetUp(self):
        super(TestAutomaticLeaveDates,self).setUp()

        self.leave_type=self.env['hr.leave.type'].create({
            'name':'AutomaticTest',
            'time_type':'leave',
            'allocation_type':'no',
            'validity_start':False,
        })

    deftest_no_attendances(self):
        calendar=self.env['resource.calendar'].create({
            'name':'NoAttendances',
            'attendance_ids':[(5,0,0)],
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,0)
            self.assertEqual(leave_form.number_of_hours_text,'0Hours')

    deftest_single_attendance_on_morning_and_afternoon(self):
        calendar=self.env['resource.calendar'].create({
            'name':'simplemorning+afternoon',
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'mondaymorning',
                                   'hour_from':8,
                                   'hour_to':12,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                               }),
                               (0,0,{
                                   'name':'mondayafternoon',
                                   'hour_from':13,
                                   'hour_to':17,
                                   'day_period':'afternoon',
                                   'dayofweek':'0',
                               })]
        })

        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,.5)
            self.assertEqual(leave_form.number_of_hours_text,'4Hours')

            leave_form.request_date_from_period='pm'

            self.assertEqual(leave_form.number_of_days_display,.5)
            self.assertEqual(leave_form.number_of_hours_text,'4Hours')

    deftest_multiple_attendance_on_morning(self):
        calendar=self.env['resource.calendar'].create({
            'name':'multimorning',
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'mondaymorning1',
                                   'hour_from':8,
                                   'hour_to':10,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                               }),
                               (0,0,{
                                   'name':'mondaymorning2',
                                   'hour_from':10.25,
                                   'hour_to':12.25,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                               }),
                               (0,0,{
                                   'name':'mondayafternoon',
                                   'hour_from':13,
                                   'hour_to':17,
                                   'day_period':'afternoon',
                                   'dayofweek':'0',
                               })]
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,.5)
            self.assertEqual(leave_form.number_of_hours_text,'4Hours')

            leave_form.request_date_from_period='pm'

            self.assertEqual(leave_form.number_of_days_display,.5)
            self.assertEqual(leave_form.number_of_hours_text,'4Hours')

    deftest_attendance_on_morning(self):
        calendar=self.env['resource.calendar'].create({
            'name':'Morningonly',
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'MondayAllday',
                                   'hour_from':8,
                                   'hour_to':16,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                               })],
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar
        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            #Askformorning
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,0.5)
            self.assertEqual(leave_form.number_of_hours_text,'8Hours')

            #Askforafternoon
            leave_form.request_date_from_period='pm'

            self.assertEqual(leave_form.number_of_days_display,0.5)
            self.assertEqual(leave_form.number_of_hours_text,'8Hours')

    deftest_attendance_next_day(self):
        self.env.user.tz='Europe/Brussels'
        calendar=self.env['resource.calendar'].create({
            'name':'autonextday',
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'tuesdaymorning',
                                   'hour_from':8,
                                   'hour_to':12,
                                   'day_period':'morning',
                                   'dayofweek':'1',
                               })]
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            #doesnotworkonmondays
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'


            self.assertEqual(leave_form.number_of_days_display,0)
            self.assertEqual(leave_form.number_of_hours_text,'0Hours')
            self.assertEqual(leave_form.date_from,datetime(2019,9,2,6,0,0))
            self.assertEqual(leave_form.date_to,datetime(2019,9,2,10,0,0))

    deftest_attendance_previous_day(self):
        self.env.user.tz='Europe/Brussels'
        calendar=self.env['resource.calendar'].create({
            'name':'autonextday',
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'mondaymorning',
                                   'hour_from':8,
                                   'hour_to':12,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                               })]
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            #doesnotworkontuesdays
            leave_form.request_date_from=date(2019,9,3)
            leave_form.request_date_to=date(2019,9,3)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'


            self.assertEqual(leave_form.number_of_days_display,0)
            self.assertEqual(leave_form.number_of_hours_text,'0Hours')
            self.assertEqual(leave_form.date_from,datetime(2019,9,3,6,0,0))
            self.assertEqual(leave_form.date_to,datetime(2019,9,3,10,0,0))

    deftest_2weeks_calendar(self):
        self.env.user.tz='Europe/Brussels'
        calendar=self.env['resource.calendar'].create({
            'name':'autonextday',
            'two_weeks_calendar':True,
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'mondaymorningoddweek',
                                   'hour_from':8,
                                   'hour_to':12,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                                   'week_type':'0',
                               }),
                               (0,0,{
                                   'name':'mondaymorningevenweek',
                                   'hour_from':10,
                                   'hour_to':12,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                                   'week_type':'1',
                               })]
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            #evenweek,works2hours
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,0.5)
            self.assertEqual(leave_form.number_of_hours_text,'2Hours')
            self.assertEqual(leave_form.date_from,datetime(2019,9,2,8,0,0))
            self.assertEqual(leave_form.date_to,datetime(2019,9,2,10,0,0))

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            #oddweek,works4hours
            leave_form.request_date_from=date(2019,9,9)
            leave_form.request_date_to=date(2019,9,9)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,0.5)
            self.assertEqual(leave_form.number_of_hours_text,'4Hours')
            self.assertEqual(leave_form.date_from,datetime(2019,9,9,6,0,0))
            self.assertEqual(leave_form.date_to,datetime(2019,9,9,10,0,0))

    deftest_2weeks_calendar_next_week(self):
        self.env.user.tz='Europe/Brussels'
        calendar=self.env['resource.calendar'].create({
            'name':'autonextday',
            'two_weeks_calendar':True,
            'attendance_ids':[(5,0,0),
                               (0,0,{
                                   'name':'mondaymorningoddweek',
                                   'hour_from':8,
                                   'hour_to':12,
                                   'day_period':'morning',
                                   'dayofweek':'0',
                                   'week_type':'0',
                               })]
        })
        employee=self.employee_emp
        employee.resource_calendar_id=calendar

        withForm(self.env['hr.leave'].with_context(default_employee_id=employee.id))asleave_form:
            leave_form.holiday_status_id=self.leave_type
            #evenweek,doesnotwork
            leave_form.request_date_from=date(2019,9,2)
            leave_form.request_date_to=date(2019,9,2)
            leave_form.request_unit_half=True
            leave_form.request_date_from_period='am'

            self.assertEqual(leave_form.number_of_days_display,0)
            self.assertEqual(leave_form.number_of_hours_text,'0Hours')
            self.assertEqual(leave_form.date_from,datetime(2019,9,2,6,0,0))
            self.assertEqual(leave_form.date_to,datetime(2019,9,2,10,0,0))
