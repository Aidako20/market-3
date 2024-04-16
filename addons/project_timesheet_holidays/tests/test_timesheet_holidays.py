#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields,SUPERUSER_ID

fromflectra.testsimportcommon,new_test_user
fromflectra.addons.hr_timesheet.tests.test_timesheetimportTestCommonTimesheet


classTestTimesheetHolidaysCreate(common.TransactionCase):

    deftest_status_create(self):
        """Ensurethatwhenastatusiscreated,itfullfillstheprojectandtaskconstrains"""
        status=self.env['hr.leave.type'].create({
            'name':'AniceLeaveType',
            'allocation_type':'no'
        })

        company=self.env.company
        self.assertEqual(status.timesheet_project_id,company.leave_timesheet_project_id,'Thedefaultprojectlinkedtothestatusshouldbethesameasthecompany')
        self.assertEqual(status.timesheet_task_id,company.leave_timesheet_task_id,'Thedefaulttasklinkedtothestatusshouldbethesameasthecompany')

    deftest_company_create(self):
        main_company=self.env.ref('base.main_company')
        user=new_test_user(self.env,login='fru',
                             groups='base.group_user,base.group_erp_manager,base.group_partner_manager',
                             company_id=main_company.id,
                             company_ids=[(6,0,main_company.ids)])
        Company=self.env['res.company']
        Company=Company.with_user(user)
        Company=Company.with_company(main_company)
        company=Company.create({'name':"WallCompany"})
        self.assertEqual(company.leave_timesheet_project_id.sudo().company_id,company,"Itshouldhavecreatedaprojectforthecompany")

classTestTimesheetHolidays(TestCommonTimesheet):

    defsetUp(self):
        super(TestTimesheetHolidays,self).setUp()

        self.employee_working_calendar=self.empl_employee.resource_calendar_id
        #leavedates:fromnextmondaytonextwednesday(toavoidcrashingtestsonweekend,when
        #thereisnoworkdaysinworkingcalendar)
        #NOTE:secondandmillisecondcanaddaworkingdays
        self.leave_start_datetime=datetime(2018,2,5,7,0,0,0) #thisismonday
        self.leave_end_datetime=self.leave_start_datetime+relativedelta(days=3)

        #allcompanyhavethoseinternalproject/task(createdbydefault)
        self.internal_project=self.env.company.leave_timesheet_project_id
        self.internal_task_leaves=self.env.company.leave_timesheet_task_id

        self.hr_leave_type_with_ts=self.env['hr.leave.type'].create({
            'name':'LeaveTypewithtimesheetgeneration',
            'allocation_type':'no',
            'timesheet_generate':True,
            'timesheet_project_id':self.internal_project.id,
            'timesheet_task_id':self.internal_task_leaves.id,
            'validity_start':False,
        })
        self.hr_leave_type_no_ts=self.env['hr.leave.type'].create({
            'name':'LeaveTypewithouttimesheetgeneration',
            'allocation_type':'no',
            'timesheet_generate':False,
            'timesheet_project_id':False,
            'timesheet_task_id':False,
            'validity_start':False,
        })

        #HROfficerallocatessomeleavestotheemployee1
        self.Requests=self.env['hr.leave'].with_context(mail_create_nolog=True,mail_notrack=True)
        self.Allocations=self.env['hr.leave.allocation'].with_context(mail_create_nolog=True,mail_notrack=True)
        self.hr_leave_allocation_with_ts=self.Allocations.sudo().create({
            'name':'Daysforlimitedcategorywithtimesheet',
            'employee_id':self.empl_employee.id,
            'holiday_status_id':self.hr_leave_type_with_ts.id,
            'number_of_days':10,
        })
        self.hr_leave_allocation_with_ts.action_approve()
        self.hr_leave_allocation_no_ts=self.Allocations.sudo().create({
            'name':'Daysforlimitedcategorywithouttimesheet',
            'employee_id':self.empl_employee.id,
            'holiday_status_id':self.hr_leave_type_no_ts.id,
            'number_of_days':10,
        })
        self.hr_leave_allocation_no_ts.action_approve()

    deftest_validate_with_timesheet(self):
        #employeecreatesaleaverequest
        number_of_days=(self.leave_end_datetime-self.leave_start_datetime).days
        holiday=self.Requests.with_user(self.user_employee).create({
            'name':'Leave1',
            'employee_id':self.empl_employee.id,
            'holiday_status_id':self.hr_leave_type_with_ts.id,
            'date_from':self.leave_start_datetime,
            'date_to':self.leave_end_datetime,
            'number_of_days':number_of_days,
        })
        holiday.with_user(SUPERUSER_ID).action_validate()
        self.assertEqual(len(holiday.timesheet_ids),number_of_days,'Numberofgeneratedtimesheetsshouldbethesameastheleaveduration(1perdaybetween%sand%s)'%(fields.Datetime.to_string(self.leave_start_datetime),fields.Datetime.to_string(self.leave_end_datetime)))

        #managerrefusetheleave
        holiday.with_user(SUPERUSER_ID).action_refuse()
        self.assertEqual(len(holiday.timesheet_ids),0,'Numberoflinkedtimesheetsshouldbezero,sincetheleaveisrefused.')

    deftest_validate_without_timesheet(self):
        #employeecreatesaleaverequest
        number_of_days=(self.leave_end_datetime-self.leave_start_datetime).days
        holiday=self.Requests.with_user(self.user_employee).create({
            'name':'Leave1',
            'employee_id':self.empl_employee.id,
            'holiday_status_id':self.hr_leave_type_no_ts.id,
            'date_from':self.leave_start_datetime,
            'date_to':self.leave_end_datetime,
            'number_of_days':number_of_days,
        })
        holiday.with_user(SUPERUSER_ID).action_validate()
        self.assertEqual(len(holiday.timesheet_ids),0,'Numberofgeneratedtimesheetsshouldbezerosincetheleavetypedoesnotgeneratetimesheet')
