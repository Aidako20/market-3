#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime

fromflectra.testsimporttagged
fromflectra.tests.commonimportSavepointCase


@tagged('company_leave')
classTestCompanyLeave(SavepointCase):
    """Testleavesforawholecompany,conflictresolutions"""

    @classmethod
    defsetUpClass(cls):
        super(TestCompanyLeave,cls).setUpClass()
        cls.company=cls.env['res.company'].create({'name':'Acompany'})

        cls.bank_holiday=cls.env['hr.leave.type'].create({
            'name':'BankHoliday',
            'responsible_id':cls.env.user.id,
            'company_id':cls.company.id,
        })

        cls.paid_time_off=cls.env['hr.leave.type'].create({
            'name':'PaidTimeOff',
            'request_unit':'day',
            'leave_validation_type':'both',
            'company_id':cls.company.id,
        })

        cls.employee=cls.env['hr.employee'].create({
            'name':'MyEmployee',
            'company_id':cls.company.id,
        })

    deftest_leave_whole_company_01(self):
        #TESTCASE1:Leavestakenindays.Takea3daysleave
        #Addacompanyleaveonthesecondday.
        #Checkthatleaveissplitinto2.

        leave=self.env['hr.leave'].create({
            'name':'Hol11',
            'employee_id':self.employee.id,
            'holiday_status_id':self.paid_time_off.id,
            'request_date_from':date(2020,1,7),
            'date_from':date(2020,1,7),
            'request_date_to':date(2020,1,9),
            'date_to':date(2020,1,9),
            'number_of_days':3,
        })
        leave._compute_date_from_to()

        company_leave=self.env['hr.leave'].create({
            'name':'BankHoliday',
            'holiday_type':'company',
            'mode_company_id':self.company.id,
            'holiday_status_id':self.bank_holiday.id,
            'date_from':date(2020,1,8),
            'request_date_from':date(2020,1,8),
            'date_to':date(2020,1,8),
            'request_date_to':date(2020,1,8),
            'number_of_days':1,
        })
        company_leave._compute_date_from_to()

        company_leave.action_validate()

        all_leaves=self.env['hr.leave'].search([('employee_id','=',self.employee.id)],order='id')
        self.assertEqual(len(all_leaves),4)
        #OriginalLeave
        self.assertEqual(leave.state,'refuse')
        #beforeleave
        self.assertEqual(all_leaves[1].date_from,datetime(2020,1,7,7,0))
        self.assertEqual(all_leaves[1].date_to,datetime(2020,1,7,16,0))
        self.assertEqual(all_leaves[1].number_of_days,1)
        self.assertEqual(all_leaves[1].state,'confirm')
        #Afterleave
        self.assertEqual(all_leaves[2].date_from,datetime(2020,1,9,7,0))
        self.assertEqual(all_leaves[2].date_to,datetime(2020,1,9,16,0))
        self.assertEqual(all_leaves[2].number_of_days,1)
        self.assertEqual(all_leaves[2].state,'confirm')
        #CompanyLeave
        self.assertEqual(all_leaves[3].date_from,datetime(2020,1,8,7,0))
        self.assertEqual(all_leaves[3].date_to,datetime(2020,1,8,16,0))
        self.assertEqual(all_leaves[3].number_of_days,1)
        self.assertEqual(all_leaves[3].state,'validate')


    deftest_leave_whole_company_02(self):
        #TESTCASE2:Leavestakeninhalf-days.Takea3daysleave
        #Addacompanyleaveonthesecondday
        #Checkthatleaveissplitinto2
        self.paid_time_off.request_unit='half_day'

        leave=self.env['hr.leave'].create({
            'name':'Hol11',
            'employee_id':self.employee.id,
            'holiday_status_id':self.paid_time_off.id,
            'request_date_from':date(2020,1,7),
            'date_from':date(2020,1,7),
            'request_date_to':date(2020,1,9),
            'date_to':date(2020,1,9),
            'number_of_days':3,
        })
        leave._compute_date_from_to()

        company_leave=self.env['hr.leave'].create({
            'name':'BankHoliday',
            'holiday_type':'company',
            'mode_company_id':self.company.id,
            'holiday_status_id':self.bank_holiday.id,
            'date_from':date(2020,1,8),
            'request_date_from':date(2020,1,8),
            'date_to':date(2020,1,8),
            'request_date_to':date(2020,1,8),
            'number_of_days':1,
        })
        company_leave._compute_date_from_to()

        company_leave.action_validate()

        all_leaves=self.env['hr.leave'].search([('employee_id','=',self.employee.id)],order='id')
        self.assertEqual(len(all_leaves),4)
        #OriginalLeave
        self.assertEqual(leave.state,'refuse')
        #beforeleave
        self.assertEqual(all_leaves[1].date_from,datetime(2020,1,7,7,0))
        self.assertEqual(all_leaves[1].date_to,datetime(2020,1,7,16,0))
        self.assertEqual(all_leaves[1].number_of_days,1)
        self.assertEqual(all_leaves[1].state,'confirm')
        #Afterleave
        self.assertEqual(all_leaves[2].date_from,datetime(2020,1,9,7,0))
        self.assertEqual(all_leaves[2].date_to,datetime(2020,1,9,16,0))
        self.assertEqual(all_leaves[2].number_of_days,1)
        self.assertEqual(all_leaves[2].state,'confirm')
        #CompanyLeave
        self.assertEqual(all_leaves[3].date_from,datetime(2020,1,8,7,0))
        self.assertEqual(all_leaves[3].date_to,datetime(2020,1,8,16,0))
        self.assertEqual(all_leaves[3].number_of_days,1)
        self.assertEqual(all_leaves[3].state,'validate')

    deftest_leave_whole_company_03(self):
        #TESTCASE3:Leavestakeninhalf-days.Takea0.5daysleave
        #Addacompanyleaveonthesameday
        #Checkthatleaverefused
        self.paid_time_off.request_unit='half_day'

        leave=self.env['hr.leave'].create({
            'name':'Hol11',
            'employee_id':self.employee.id,
            'holiday_status_id':self.paid_time_off.id,
            'request_date_from':date(2020,1,7),
            'request_date_to':date(2020,1,7),
            'number_of_days':0.5,
            'request_unit_half':True,
            'request_date_from_period':'am',

        })
        leave._compute_date_from_to()

        company_leave=self.env['hr.leave'].create({
            'name':'BankHoliday',
            'holiday_type':'company',
            'mode_company_id':self.company.id,
            'holiday_status_id':self.bank_holiday.id,
            'date_from':date(2020,1,7),
            'request_date_from':date(2020,1,7),
            'date_to':date(2020,1,7),
            'request_date_to':date(2020,1,7),
            'number_of_days':1,
        })
        company_leave._compute_date_from_to()

        company_leave.action_validate()

        all_leaves=self.env['hr.leave'].search([('employee_id','=',self.employee.id)],order='id')
        self.assertEqual(len(all_leaves),2)
        #OriginalLeave
        self.assertEqual(leave.state,'refuse')
        #CompanyLeave
        self.assertEqual(all_leaves[1].date_from,datetime(2020,1,7,7,0))
        self.assertEqual(all_leaves[1].date_to,datetime(2020,1,7,16,0))
        self.assertEqual(all_leaves[1].number_of_days,1)
        self.assertEqual(all_leaves[1].state,'validate')

    deftest_leave_whole_company_04(self):
        #TESTCASE4:Leavestakenindays.Takea1daysleave
        #Addacompanyleaveonthesameday
        #Checkthatleaveisrefused
        self.paid_time_off.request_unit='day'

        leave=self.env['hr.leave'].create({
            'name':'Hol11',
            'employee_id':self.employee.id,
            'holiday_status_id':self.paid_time_off.id,
            'request_date_from':date(2020,1,9),
            'request_date_to':date(2020,1,9),
            'number_of_days':1,

        })
        leave._compute_date_from_to()

        company_leave=self.env['hr.leave'].create({
            'name':'BankHoliday',
            'holiday_type':'company',
            'mode_company_id':self.company.id,
            'holiday_status_id':self.bank_holiday.id,
            'date_from':date(2020,1,9),
            'request_date_from':date(2020,1,9),
            'date_to':date(2020,1,9),
            'request_date_to':date(2020,1,9),
            'number_of_days':1,
        })
        company_leave._compute_date_from_to()

        company_leave.action_validate()

        all_leaves=self.env['hr.leave'].search([('employee_id','=',self.employee.id)],order='id')
        self.assertEqual(len(all_leaves),2)
        #OriginalLeave
        self.assertEqual(leave.state,'refuse')
        #CompanyLeave
        self.assertEqual(all_leaves[1].date_from,datetime(2020,1,9,7,0))
        self.assertEqual(all_leaves[1].date_to,datetime(2020,1,9,16,0))
        self.assertEqual(all_leaves[1].number_of_days,1)
        self.assertEqual(all_leaves[1].state,'validate')

    deftest_leave_whole_company_06(self):
        #Testcase6:Leavestakenindays.Buttheemployee
        #onlyworksonMonday,WednesdayandFriday
        #Takesatimeoffforalltheweek(3days),shouldbesplit

        self.employee.resource_calendar_id.write({'attendance_ids':[
            (5,0,0),
            (0,0,{'name':'MondayMorning','dayofweek':'0','hour_from':8,'hour_to':12,'day_period':'morning'}),
            (0,0,{'name':'MondayAfternoon','dayofweek':'0','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
            (0,0,{'name':'WednesdayMorning','dayofweek':'2','hour_from':8,'hour_to':12,'day_period':'morning'}),
            (0,0,{'name':'WednesdayAfternoon','dayofweek':'2','hour_from':13,'hour_to':17,'day_period':'afternoon'}),
            (0,0,{'name':'FridayMorning','dayofweek':'4','hour_from':8,'hour_to':12,'day_period':'morning'}),
            (0,0,{'name':'FridayAfternoon','dayofweek':'4','hour_from':13,'hour_to':17,'day_period':'afternoon'})
        ]})

        leave=self.env['hr.leave'].create({
            'name':'Hol11',
            'employee_id':self.employee.id,
            'holiday_status_id':self.paid_time_off.id,
            'request_date_from':date(2020,1,6),
            'request_date_to':date(2020,1,10),
            'number_of_days':3,
        })
        leave._compute_date_from_to()

        company_leave=self.env['hr.leave'].create({
            'name':'BankHoliday',
            'holiday_type':'company',
            'mode_company_id':self.company.id,
            'holiday_status_id':self.bank_holiday.id,
            'date_from':date(2020,1,10),
            'request_date_from':date(2020,1,10),
            'date_to':date(2020,1,10),
            'request_date_to':date(2020,1,10),
            'number_of_days':1,
        })
        company_leave._compute_date_from_to()
        company_leave.action_validate()

        all_leaves=self.env['hr.leave'].search([('employee_id','=',self.employee.id)],order='id')
        self.assertEqual(len(all_leaves),3)
        #OriginalLeave
        self.assertEqual(leave.state,'refuse')
        #beforeleave
        self.assertEqual(all_leaves[1].date_from,datetime(2020,1,6,7,0))
        self.assertEqual(all_leaves[1].date_to,datetime(2020,1,9,16,0))
        self.assertEqual(all_leaves[1].number_of_days,2)
        self.assertEqual(all_leaves[1].state,'confirm')
        #CompanyLeave
        self.assertEqual(all_leaves[2].date_from,datetime(2020,1,10,7,0))
        self.assertEqual(all_leaves[2].date_to,datetime(2020,1,10,16,0))
        self.assertEqual(all_leaves[2].number_of_days,1)
        self.assertEqual(all_leaves[2].state,'validate')

    deftest_leave_whole_company_07(self):
        #TestCase7:Trytocreateabankholidaysforalotof
        #employees,andchecktheperformances
        #100employees-15alreadyonholidaysthatday

        employees=self.env['hr.employee'].create([{
            'name':'Employee%s'%i,
            'company_id':self.company.id
        }foriinrange(100)])

        leaves=self.env['hr.leave'].create([{
            'name':'Holiday-%s'%employee.name,
            'employee_id':employee.id,
            'holiday_status_id':self.paid_time_off.id,
            'request_date_from':date(2020,3,29),
            'date_from':datetime(2020,3,29,7,0,0),
            'request_date_to':date(2020,4,1),
            'date_to':datetime(2020,4,1,19,0,0),
            'number_of_days':3,
        }foremployeeinemployees[0:15]])
        leaves._compute_date_from_to()

        company_leave=self.env['hr.leave'].create({
            'name':'BankHoliday',
            'holiday_type':'company',
            'mode_company_id':self.company.id,
            'holiday_status_id':self.bank_holiday.id,
            'date_from':date(2020,4,1),
            'request_date_from':date(2020,4,1),
            'date_to':date(2020,4,1),
            'request_date_to':date(2020,4,1),
            'number_of_days':1,
        })
        company_leave._compute_date_from_to()

        count=734
        withself.assertQueryCount(__system__=count,admin=count):
            #Originalquerycount:1987
            #Withouttracking/activitycontextkeys:5154
            company_leave.action_validate()

        leaves=self.env['hr.leave'].search([('holiday_status_id','=',self.bank_holiday.id)])
        self.assertEqual(len(leaves),102)
