#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttests
fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon
fromflectra.exceptionsimportAccessError,UserError


@tests.tagged('access_rights','post_install','-at_install')
classTestAllocationRights(TestHrHolidaysCommon):

    defsetUp(self):
        super().setUp()
        self.rd_dept.manager_id=False
        self.hr_dept.manager_id=False
        self.employee_emp.parent_id=False
        self.employee_emp.leave_manager_id=False

        self.lt_validation_hr=self.env['hr.leave.type'].create({
            'name':'Validation=HR',
            'allocation_validation_type':'hr',
            'allocation_type':'fixed_allocation',
            'validity_start':False,
        })

        self.lt_validation_manager=self.env['hr.leave.type'].create({
            'name':'Validation=manager',
            'allocation_validation_type':'manager',
            'allocation_type':'fixed_allocation',
            'validity_start':False,
        })

        self.lt_validation_both=self.env['hr.leave.type'].create({
            'name':'Validation=both',
            'allocation_validation_type':'both',
            'allocation_type':'fixed_allocation',
            'validity_start':False,
        })

    defrequest_allocation(self,user,values={}):
        values=dict(values,**{
            'name':'Allocation',
            'number_of_days':1,
        })
        returnself.env['hr.leave.allocation'].with_user(user).create(values)


classTestAccessRightsSimpleUser(TestAllocationRights):

    deftest_simple_user_request_allocation(self):
        """Asimpleusercanrequestanallocationbutnotapproveit"""
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_employee.id,values)
        withself.assertRaises(UserError):
            allocation.action_approve()

    deftest_simple_user_request_fixed_allocation(self):
        """AsimpleusercannotrequestanallocationifsetbyHR"""
        self.lt_validation_hr.allocation_type='fixed'
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        withself.assertRaises(AccessError):
            self.request_allocation(self.user_employee.id,values)

    deftest_simple_user_reset_to_draft(self):
        """Asimpleusercanresettodraftonlyhisownallocation"""
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_employee.id,values)
        self.assertEqual(allocation.state,'confirm')
        allocation.action_draft()
        self.assertEqual(allocation.state,'draft',"Itshouldberesettodraftstate")


classTestAccessRightsEmployeeManager(TestAllocationRights):

    defsetUp(self):
        super().setUp()
        self.managed_employee=self.env['hr.employee'].create({
            'name':'JollyJumper',
            'leave_manager_id':self.user_employee.id,
        })

    deftest_manager_request_allocation_other(self):
        """Amanagercannotrequestandapproveanallocationforemployeeshedoesn'tmanage"""
        values={
            'employee_id':self.employee_hruser.id,
            'holiday_status_id':self.lt_validation_manager.id,
        }
        withself.assertRaises(AccessError):
            self.request_allocation(self.user_employee.id,values) #userisnottheemployee'smanager

    deftest_manager_approve_request_allocation(self):
        """Amanagercanrequestandapproveanallocationformanagedemployees"""
        values={
            'employee_id':self.managed_employee.id,
            'holiday_status_id':self.lt_validation_manager.id,
        }
        allocation=self.request_allocation(self.user_employee.id,values)
        allocation.action_approve()
        self.assertEqual(allocation.state,'validate',"Theallocationshouldbevalidated")

    deftest_manager_refuse_request_allocation(self):
        """Amanagercanrequestandrefuseanallocationformanagedemployees"""
        values={
            'employee_id':self.managed_employee.id,
            'holiday_status_id':self.lt_validation_manager.id,
        }
        allocation=self.request_allocation(self.user_employee.id,values)
        allocation.action_refuse()
        self.assertEqual(allocation.state,'refuse',"Theallocationshouldbevalidated")

    deftest_manager_batch_allocation(self):
        """Amanagercannotcreatebatchallocation"""
        values={
            'holiday_status_id':self.lt_validation_manager.id,
            'holiday_type':'company',
            'mode_company_id':self.user_employee.company_id.id,
        }
        withself.assertRaises(AccessError):
            self.request_allocation(self.user_employee.id,values)

    deftest_manager_approve_own(self):
        """Amanagercannotapprovehisownallocation"""
        values={
            'employee_id':self.user_employee.employee_id.id,
            'holiday_status_id':self.lt_validation_manager.id,
        }
        allocation=self.request_allocation(self.user_employee.id,values)
        withself.assertRaises(UserError):
            allocation.action_approve()

    deftest_manager_only_first_approval(self):
        """Amanagercanonlydothefirstapproval"""
        values={
            'employee_id':self.managed_employee.id,
            'holiday_status_id':self.lt_validation_both.id,
        }
        allocation=self.request_allocation(self.user_employee.id,values)
        allocation.action_approve()
        withself.assertRaises(UserError):
            allocation.action_validate()


classTestAccessRightsHolidayUser(TestAllocationRights):

    deftest_holiday_user_request_allocation(self):
        """Aholidayusercanrequestandapproveanallocationforanyemployee"""
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_hruser.id,values)
        allocation.action_approve()
        self.assertEqual(allocation.state,'validate',"Itshouldhavebeenvalidated")

    deftest_holiday_user_request_fixed_allocation(self):
        """AholidayusercanrequestandapproveanallocationifsetbyHR"""
        self.lt_validation_hr.allocation_type='fixed'
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_hruser.id,values)
        allocation.action_approve()
        self.assertEqual(allocation.state,'validate',"Itshouldhavebeenvalidated")

    deftest_holiday_user_both_second_approval(self):
        """Aholidayusercanonlydothesecondapprovalwhendoublevalidation"""
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_both.id,
        }
        allocation=self.request_allocation(self.user_hruser.id,values)
        withself.assertRaises(UserError):
            allocation.action_approve()
        allocation.sudo().action_approve() #Firstapprovalbysomeoneelse
        allocation.action_validate()
        self.assertEqual(allocation.state,'validate',"Itshouldhavebeenvalidated")

    deftest_holiday_user_batch_allocation(self):
        """Aholidayusercannotcreateabatchallocation"""
        values={
            'holiday_status_id':self.lt_validation_hr.id,
            'holiday_type':'company',
            'mode_company_id':self.user_employee.company_id.id,
        }
        withself.assertRaises(AccessError):
            self.request_allocation(self.user_hruser.id,values)

    deftest_holiday_user_cannot_approve_own(self):
        """Aholidayusercannotapprovehisownallocation"""
        values={
            'employee_id':self.employee_hruser.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_hruser.id,values)
        withself.assertRaises(UserError):
            allocation.action_approve()


classTestAccessRightsHolidayManager(TestAllocationRights):

    deftest_holiday_manager_can_approve_own(self):
        """Aholidaymanagercanapprovehisownallocation"""
        values={
            'employee_id':self.employee_hrmanager.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_hrmanager.id,values)
        allocation.action_approve()
        self.assertEqual(allocation.state,'validate',"Itshouldhavebeenvalidated")

    deftest_holiday_manager_both_validation(self):
        """Aholidaymanagercanperformbothvalidation"""
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_both.id,
        }
        allocation=self.request_allocation(self.user_hrmanager.id,values)
        allocation.action_approve()
        self.assertEqual(allocation.state,'validate1',"Itshouldhavebeenvalidatedonetime")
        allocation.action_validate()
        self.assertEqual(allocation.state,'validate',"Itshouldhavebeencompletelyvalidated")

    deftest_holiday_manager_refuse_validated(self):
        """Aholidaymanagercanrefuseavalidatedallocation"""
        values={
            'employee_id':self.employee_emp.id,
            'holiday_status_id':self.lt_validation_hr.id,
        }
        allocation=self.request_allocation(self.user_hrmanager.id,values)
        allocation.action_approve()
        self.assertEqual(allocation.state,'validate',"Itshouldhavebeenvalidated")
        allocation.action_refuse()
        self.assertEqual(allocation.state,'refuse',"Itshouldhavebeenrefused")
