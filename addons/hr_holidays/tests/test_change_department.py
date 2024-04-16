#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon


classTestChangeDepartment(TestHrHolidaysCommon):
    deftest_employee_change_department_request_change_department(self):
        self.HolidaysEmployeeGroup=self.env['hr.leave'].with_user(self.user_employee_id)

        HolidayStatusManagerGroup=self.env['hr.leave.type'].with_user(self.user_hrmanager_id)
        self.holidays_status_1=HolidayStatusManagerGroup.create({
            'name':'NotLimitedHR',
            'allocation_type':'no',
            'validity_start':False,
        })

        defcreate_holiday(name,start,end):
            returnself.HolidaysEmployeeGroup.create({
                'name':name,
                'employee_id':self.employee_emp_id,
                'holiday_status_id':self.holidays_status_1.id,
                'date_from':(datetime.today()+relativedelta(days=start)).strftime('%Y-%m-%d%H:%M'),
                'date_to':datetime.today()+relativedelta(days=end),
                'number_of_days':end-start,
            })

        #Nonapprovedleaverequestchangedepartment
        self.employee_emp.department_id=self.rd_dept
        hol1_employee_group=create_holiday("hol1",1,2)
        self.employee_emp.department_id=self.hr_dept
        self.assertEqual(hol1_employee_group.department_id,self.hr_dept,'hr_holidays:nonapprovedleaverequestshouldchangedepartmentifemployeechangedepartment')

        #Approvedpassedleaverequestchangedepartment
        self.employee_emp.department_id=self.hr_dept
        hol2_employee_group=create_holiday("hol2",-4,-3)
        hol2_user_group=hol2_employee_group.with_user(self.user_hruser_id)
        hol2_user_group.action_approve()
        self.employee_emp.department_id=self.rd_dept
        self.assertEqual(hol2_employee_group.department_id,self.hr_dept,'hr_holidays:approvedpassedleaverequestshouldstayinpreviousdepartmentifemployeechangedepartment')

        #Approvedfuturleaverequestchangedepartment
        self.employee_emp.department_id=self.hr_dept
        hol22_employee_group=create_holiday("hol22",3,4)
        hol22_user_group=hol22_employee_group.with_user(self.user_hruser_id)
        hol22_user_group.action_approve()
        self.employee_emp.department_id=self.rd_dept
        self.assertEqual(hol22_employee_group.department_id,self.rd_dept,'hr_holidays:approvedfuturleaverequestshouldchangedepartmentifemployeechangedepartment')

        #Refusedpassedleaverequestchangedepartment
        self.employee_emp.department_id=self.rd_dept
        hol3_employee_group=create_holiday("hol3",-6,-5)
        hol3_user_group=hol3_employee_group.with_user(self.user_hruser_id)
        hol3_user_group.action_refuse()
        self.employee_emp.department_id=self.hr_dept#Changedepartment
        self.assertEqual(hol3_employee_group.department_id,self.rd_dept,'hr_holidays:refusedpassedleaverequestshouldstayinpreviousdepartmentifemployeechangedepartment')

        #Refusedfuturleaverequestchangedepartment
        self.employee_emp.department_id=self.rd_dept
        hol32_employee_group=create_holiday("hol32",5,6)
        hol32_user_group=hol32_employee_group.with_user(self.user_hruser_id)
        hol32_user_group.action_refuse()
        self.employee_emp.department_id=self.hr_dept#Changedepartment
        self.assertEqual(hol32_employee_group.department_id,self.hr_dept,'hr_holidays:refusedfuturleaverequestshouldchangedepartmentifemployeechangedepartment')
