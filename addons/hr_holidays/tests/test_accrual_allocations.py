#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,time
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields

fromflectra.toolsimportmute_logger

fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon


classTestAccrualAllocations(TestHrHolidaysCommon):
    defsetUp(self):
        super(TestAccrualAllocations,self).setUp()

        #Makesurewehavetherightstocreate,validateanddeletetheleaves,leavetypesandallocations
        LeaveType=self.env['hr.leave.type'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True)

        self.accrual_type=LeaveType.create({
            'name':'accrual',
            'allocation_type':'fixed',
            'validity_start':False,
        })

        self.unpaid_type=LeaveType.create({
            'name':'unpaid',
            'allocation_type':'no',
            'unpaid':True,
            'validity_start':False,
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

    deftest_accrual_base_no_leaves(self):
        """Testifwecanallocatesomeleavesaccruallytoanemployee"""
        alloc=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True).create({
            'name':'Accrualallocationforemployee',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':1,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'weeks',
        })
        alloc.action_approve()
        alloc._update_accrual()

        self.assertEqual(alloc.number_of_days,1,'Employeeshouldhavebeenallocatedoneleaveday')

    deftest_accrual_base_leaves(self):
        """Testiftheaccrualallocationtaketheunpaidleavesintoaccountwhenallocatingleaves"""
        alloc=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True).create({
            'name':'Accrualallocationforemployeewithleaves',
            'employee_id':self.employee_hruser_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':1,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'weeks',
        })

        alloc.action_approve()

        employee=self.env['hr.employee'].browse(self.employee_hruser_id)
        #Gettingthepreviousworkdate
        df=employee.resource_calendar_id.plan_days(-2,fields.Datetime.now()).date()

        leave=self.env['hr.leave'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True).create({
            'name':'Leaveforhruser',
            'employee_id':self.employee_hruser_id,
            'holiday_status_id':self.unpaid_type.id,
            'date_from':datetime.combine(df,time(0,0,0)),
            'date_to':datetime.combine(df+relativedelta(days=1),time(0,0,0)),
            'number_of_days':1,
        })

        leave.action_approve()

        alloc._update_accrual()

        self.assertEqual(alloc.number_of_days,.8,'Asemployeetooksomeunpaidleaveslastweek,heshouldbeallocatedonly.8days')

    deftest_accrual_many(self):
        """
            Testdifferentconfigurationofaccrualallocations
        """
        Allocation=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True)

        alloc_0=Allocation.create({
            'name':'1dayper2weeks',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':1,
            'interval_number':2,
            'unit_per_interval':'days',
            'interval_unit':'weeks',
        })

        alloc_1=Allocation.create({
            'name':'4hoursperweek',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':4,
            'interval_number':1,
            'unit_per_interval':'hours',
            'interval_unit':'weeks',
        })

        alloc_2=Allocation.create({
            'name':'2dayper1month',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':2,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'months',
        })

        alloc_3=Allocation.create({
            'name':'20daysperyear',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':20,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'years',
        })

        (alloc_0|alloc_1|alloc_2|alloc_3).action_approve()

        Allocation._update_accrual()

        self.assertEqual(alloc_0.number_of_days,1)
        self.assertEqual(alloc_1.number_of_days,.5)
        self.assertEqual(alloc_2.number_of_days,2)
        self.assertEqual(alloc_3.number_of_days,20)

    deftest_accrual_new_employee(self):
        """
            Testifaccrualallocationtakesintoaccountthecreationdate
            ofanemployee
        """
        Allocation=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True)

        self.set_employee_create_date(self.employee_emp_id,fields.Datetime.to_string(fields.Datetime.now()))

        alloc_0=Allocation.create({
            'name':'oneshotonekill',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':1,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'weeks',
        })

        alloc_0.action_approve()

        Allocation._update_accrual()

        self.assertEqual(alloc_0.number_of_days,0,'Employeeisnewheshouldnotgetanyaccrualleaves')

    deftest_accrual_multi(self):
        """Testifthecrondoesnotallocateleaveseverytimeit'scalledbutonlywhennecessary"""
        alloc=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True).create({
            'name':'2daysperweek',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'number_of_days':0,
            'number_per_interval':1,
            'interval_number':2,
            'unit_per_interval':'days',
            'interval_unit':'weeks',
        })
        alloc.action_approve()
        alloc._update_accrual()
        alloc._update_accrual()

        self.assertEqual(alloc.number_of_days,1,'Crononlyallocates1dayseverytwoweeks')

    deftest_accrual_validation(self):
        """
            Testifcrondoesnotallocatepastit'svaliditydate
        """
        Allocation=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True)

        alloc_0=Allocation.create({
            'name':'20daysperyear',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'number_of_days':0,
            'number_per_interval':20,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'years',
            'date_to':fields.Datetime.from_string('2015-02-0300:00:00'),
        })

        alloc_0.action_approve()

        Allocation._update_accrual()

        self.assertEqual(alloc_0.number_of_days,0,'Cronvaliditypassed,shouldnotallocateanyleave')

    deftest_accrual_balance_limit(self):
        """Testifaccrualallocationdoesnotallocatemorethanthebalancelimit"""
        allocation=self.env['hr.leave.allocation'].with_user(self.user_hrmanager_id).with_context(tracking_disable=True).create({
            'name':'accrual5max',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.accrual_type.id,
            'allocation_type':'accrual',
            'accrual_limit':5,
            'number_of_days':0,
            'number_per_interval':6,
            'interval_number':1,
            'unit_per_interval':'days',
            'interval_unit':'weeks',
        })
        allocation.action_approve()
        allocation._update_accrual()

        self.assertEqual(allocation.number_of_days,5,'Shouldhaveallocatedonly5daysasbalancelimitis5')
