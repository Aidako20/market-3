#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.addons.hr.tests.commonimportTestHrCommon


classTestHrEmployee(TestHrCommon):

    deftest_employee_resource(self):
        _tz='Pacific/Apia'
        self.res_users_hr_officer.company_id.resource_calendar_id.tz=_tz
        Employee=self.env['hr.employee'].with_user(self.res_users_hr_officer)
        employee_form=Form(Employee)
        employee_form.name='RaoulGrosbedon'
        employee_form.work_email='raoul@example.com'
        employee=employee_form.save()
        self.assertEqual(employee.tz,_tz)

    deftest_employee_from_user(self):
        _tz='Pacific/Apia'
        _tz2='America/Tijuana'
        self.res_users_hr_officer.company_id.resource_calendar_id.tz=_tz
        self.res_users_hr_officer.tz=_tz2
        Employee=self.env['hr.employee'].with_user(self.res_users_hr_officer)
        employee_form=Form(Employee)
        employee_form.name='RaoulGrosbedon'
        employee_form.work_email='raoul@example.com'
        employee_form.user_id=self.res_users_hr_officer
        employee=employee_form.save()
        self.assertEqual(employee.name,'RaoulGrosbedon')
        self.assertEqual(employee.work_email,self.res_users_hr_officer.email)
        self.assertEqual(employee.tz,self.res_users_hr_officer.tz)

    deftest_employee_from_user_tz_no_reset(self):
        _tz='Pacific/Apia'
        self.res_users_hr_officer.tz=False
        Employee=self.env['hr.employee'].with_user(self.res_users_hr_officer)
        employee_form=Form(Employee)
        employee_form.name='RaoulGrosbedon'
        employee_form.work_email='raoul@example.com'
        employee_form.tz=_tz
        employee_form.user_id=self.res_users_hr_officer
        employee=employee_form.save()
        self.assertEqual(employee.name,'RaoulGrosbedon')
        self.assertEqual(employee.work_email,self.res_users_hr_officer.email)
        self.assertEqual(employee.tz,_tz)
