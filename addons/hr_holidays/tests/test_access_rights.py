#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimporttests
fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.toolsimportmute_logger


@tests.tagged('access_rights','post_install','-at_install')
classTestHrHolidaysAccessRightsCommon(TestHrHolidaysCommon):
    defsetUp(self):
        super(TestHrHolidaysAccessRightsCommon,self).setUp()
        self.leave_type=self.env['hr.leave.type'].create({
            'name':'Unlimited',
            'leave_validation_type':'hr',
            'allocation_type':'no',
            'validity_start':False,
        })
        self.rd_dept.manager_id=False
        self.hr_dept.manager_id=False
        self.employee_emp.parent_id=False
        self.employee_leave=self.env['hr.leave'].with_user(self.user_employee_id).create({
            'name':'Test',
            'holiday_status_id':self.leave_type.id,
            'department_id':self.employee_emp.department_id.id,
            'employee_id':self.employee_emp.id,
            'date_from':datetime.now(),
            'date_to':datetime.now()+relativedelta(days=1),
            'number_of_days':1,
        })

        self.lt_no_validation=self.env['hr.leave.type'].create({
            'name':'Validation=no_validation',
            'leave_validation_type':'hr',
            'allocation_type':'no',
            'validity_start':False,
        })

        self.lt_validation_hr=self.env['hr.leave.type'].create({
            'name':'Validation=HR',
            'leave_validation_type':'hr',
            'allocation_type':'no',
            'validity_start':False,
        })

        self.lt_validation_manager=self.env['hr.leave.type'].create({
            'name':'Validation=manager',
            'leave_validation_type':'hr',
            'allocation_type':'no',
            'validity_start':False,
        })

        self.lt_validation_both=self.env['hr.leave.type'].create({
            'name':'Validation=both',
            'leave_validation_type':'hr',
            'allocation_type':'no',
            'validity_start':False,
        })

        self.draft_status=[
            self.lt_validation_hr,
            self.lt_validation_manager,
            self.lt_validation_both
        ]

        self.confirm_status=[
            self.lt_no_validation,
            self.lt_validation_hr,
            self.lt_validation_manager,
            self.lt_validation_both
        ]

    defrequest_leave(self,user_id,date_from,number_of_days,values=None):
        values=dict(valuesor{},**{
            'date_from':date_from,
            'date_to':date_from+relativedelta(days=number_of_days),
            'number_of_days':number_of_days,
        })
        returnself.env['hr.leave'].with_user(user_id).create(values)


@tests.tagged('access_rights','access_rights_states')
classTestAcessRightsStates(TestHrHolidaysAccessRightsCommon):
    #******************************************************
    #Actiondraft
    #******************************************************

    deftest_draft_status(self):
        """
            Weshouldonlybeabletodraftaleavethatis
            inconfirmorrefusestate
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'Ranoi',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.action_draft()

            values={
                'name':'Ranoi',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=20+i),1,values)
            #thestatehastobesettodraftinawritebecauseitisinitializedtoconfirmifithasvalidation
            leave.write({'state':'draft'})
            withself.assertRaises(UserError):
                leave.action_draft()

    deftest_base_user_draft_his_leave(self):
        """
            Shouldbeabletodrafthisownleave
            whatevertheholiday_status_id
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_employee.id).action_draft()

    deftest_base_user_draft_other_employee_leave(self):
        """
            Shouldnotbeabletodrafttheleaveofsomeoneelse
            whatevertheholiday_status_id
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            withself.assertRaises(UserError):
                leave.with_user(self.user_employee.id).action_draft()

    deftest_base_user_draft_other_employee_leave_and_is_leave_manager_id(self):
        """
            Shouldnotbeabletodrafttheleaveofsomeoneelse
            evenwhenbeingtheleavemanageridforthisperson
            whatevertheholiday_status_id
        """
        self.employee_hruser.write({'leave_manager_id':self.user_employee.id})
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            withself.assertRaises(UserError):
                leave.with_user(self.user_employee.id).action_draft()

    deftest_base_user_draft_self_and_is_leave_manager_id(self):
        """
            Shouldbeabletodrafthisownleave
            evenwhenbeingleavemanagerid
            whatevertheholiday_status_id
        """
        self.employee_emp.write({'leave_manager_id':self.user_employee.id})
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_employee.id).action_draft()

    deftest_base_user_draft_refused_leave(self):
        """
            Shouldnotbeabletodraftarefusedleave
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.action_refuse()
            withself.assertRaises(UserError):
                leave.with_user(self.user_employee.id).action_draft()

    deftest_base_user_draft_current_leave(self):
        """
            Shouldnotbeabletodraftapassedleave
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=-20+i),1,values)
            withself.assertRaises(UserError):
                leave.with_user(self.user_employee.id).action_draft()

    deftest_holiday_user_draft_his_leave(self):
        """
            Shouldbeabletodrafthisownleave
            whatevertheholiday_status_id
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_hruser.id).action_draft()

    deftest_holiday_user_draft_other_employee_leave(self):
        """
            Shouldnotbeabletodraftotheremployeeleave
            whatevertheholiday_status_id
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            withself.assertRaises(UserError):
                leave.with_user(self.user_hruser.id).action_draft()

    deftest_holiday_user_draft_other_employee_leave_and_is_leave_manager_id(self):
        """
            Shouldnotbeabletodraftotheremployeeleave
            evenifheistheleavemanagerid
            whatevertheholiday_status_id
        """
        self.employee_emp.write({'leave_manager_id':self.user_hruser.id})
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_emp.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            withself.assertRaises(UserError):
                leave.with_user(self.user_hruser.id).action_draft()

    deftest_holiday_user_draft_self_and_is_manager_id(self):
        """
            Shouldbeabletodrafthisownleave
            evenifheisleavemanagerid
            whatevertheholiday_status_id
        """
        self.employee_hruser.write({'leave_manager_id':self.user_hruser.id})
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_hruser.id).action_draft()

    deftest_holiday_user_draft_refused_leave(self):
        """
            Shouldnotbeabletodraftarefusedleave
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.action_refuse()
            withself.assertRaises(UserError):
                leave.with_user(self.user_hruser.id).action_draft()

    deftest_holiday_user_draft_current_leave(self):
        """
            Shouldnotbeabletodraftapassedleave
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=-20+i),1,values)
            withself.assertRaises(UserError):
                leave.with_user(self.user_hruser.id).action_draft()

    deftest_holiday_manager_draft_his_leave(self):
        """
            Theholidaymanagershouldbeabletodoeverything
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hrmanager.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_hrmanager.id).action_draft()

    deftest_holiday_manager_draft_other_employee_leave(self):
        """
            Theholidaymanagershouldbeabletodoeverything
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_hrmanager.id).action_draft()

    deftest_holiday_manager_draft_other_employee_leave_and_is_leave_manager_id(self):
        """
            Theholidaymanagershouldbeabletodoeverything
        """
        self.employee_hruser.write({'leave_manager_id':self.user_hrmanager.id})
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_hrmanager.id).action_draft()

    deftest_holiday_manager_draft_self_and_is_manager_id(self):
        """
            Theholidaymanagershouldbeabletodoeverything
        """
        self.employee_hrmanager.write({'leave_manager_id':self.user_hrmanager.id})
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hrmanager.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.with_user(self.user_hrmanager.id).action_draft()

    deftest_holiday_manager_draft_refused_leave(self):
        """
            Theholidaymanagershouldbeabletodoeverything
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=5+i),1,values)
            leave.action_refuse()
            leave.with_user(self.user_hrmanager.id).action_draft()

    deftest_holiday_manager_draft_current_leave(self):
        """
            Theholidaymanagershouldbeabletodoeverything
        """
        fori,statusinenumerate(self.draft_status):
            values={
                'name':'RandomLeave',
                'employee_id':self.employee_hruser.id,
                'holiday_status_id':status.id,
            }
            leave=self.request_leave(1,datetime.today()+relativedelta(days=-20+i),1,values)
            leave.with_user(self.user_hrmanager.id).action_draft()

@tests.tagged('access_rights','access_rights_create')
classTestAccessRightsCreate(TestHrHolidaysAccessRightsCommon):
    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_base_user_create_self(self):
        """Asimpleusercancreatealeaveforhimself"""
        values={
            'name':'Hol10',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.leave_type.id,
        }
        self.request_leave(self.user_employee_id,datetime.today()+relativedelta(days=5),1,values)

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_base_user_create_other(self):
        """Asimpleusercannotcreatealeaveforsomeoneelse"""
        values={
            'name':'Hol10',
            'employee_id':self.employee_hruser_id,
            'holiday_status_id':self.leave_type.id,
        }
        withself.assertRaises(AccessError):
            self.request_leave(self.user_employee_id,datetime.today()+relativedelta(days=5),1,values)


    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_base_user_create_batch(self):
        """Asimpleusercannotcreatealeaveinbacthmode(bycompany,bydepartment,bytag)"""
        values={
            'name':'Hol10',
            'holiday_status_id':self.leave_type.id,
            'holiday_type':'company',
            'mode_company_id':1,
        }
        withself.assertRaises(AccessError):
            self.request_leave(self.user_employee_id,datetime.today()+relativedelta(days=5),1,values)

    #hr_holidays.group_hr_holidays_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_holidays_user_create_self(self):
        """Aholidaysusercancreatealeaveforhimself"""
        values={
            'name':'Hol10',
            'employee_id':self.employee_hruser_id,
            'holiday_status_id':self.leave_type.id,
        }
        self.request_leave(self.user_hruser_id,datetime.today()+relativedelta(days=5),1,values)

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_holidays_user_create_other(self):
        """Aholidaysusercancreatealeaveforsomeoneelse"""
        values={
            'name':'Hol10',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.leave_type.id,
        }
        self.request_leave(self.user_hruser_id,datetime.today()+relativedelta(days=5),1,values)

    #hr_holidays.group_hr_holidays_manager

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_holidays_manager_create_self(self):
        """Aholidaysmanagercancreatealeaveforhimself"""
        values={
            'name':'Hol10',
            'employee_id':self.employee_hrmanager_id,
            'holiday_status_id':self.leave_type.id,
        }
        self.request_leave(self.user_hrmanager_id,datetime.today()+relativedelta(days=5),1,values)

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_holidays_manager_create_other(self):
        """Aholidaysmanagercancreatealeaveforsomeoneelse"""
        values={
            'name':'Hol10',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.leave_type.id,
        }
        self.request_leave(self.user_hrmanager_id,datetime.today()+relativedelta(days=5),1,values)

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_holidays_manager_create_batch(self):
        """Aholidaysmanagercancreatealeaveinbacthmode(bycompany,bydepartment,bytag)"""
        values={
            'name':'Hol10',
            'holiday_status_id':self.leave_type.id,
            'holiday_type':'company',
            'mode_company_id':1,
        }
        self.request_leave(self.user_hrmanager_id,datetime.today()+relativedelta(days=5),1,values)


@tests.tagged('access_rights','access_rights_read')
classTestAccessRightsRead(TestHrHolidaysAccessRightsCommon):
    #base.group_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_read_by_user_other(self):
        """Usersshouldnotbeabletoreadotherpeoplerequests"""
        other_leave=self.env['hr.leave'].with_user(self.user_hruser).create({
            'name':'Test',
            'holiday_status_id':self.leave_type.id,
            'department_id':self.employee_hruser.department_id.id,
            'employee_id':self.employee_hruser.id,
            'date_from':datetime.now(),
            'date_to':datetime.now()+relativedelta(days=1),
            'number_of_days':1,
        })
        withself.assertRaises(AccessError),self.cr.savepoint():
            res=other_leave.with_user(self.user_employee_id).read(['number_of_days','state','name'])

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_read_by_user_other_browse(self):
        """Usersshouldnotbeabletobrowseotherpeoplerequests"""
        other_leave=self.env['hr.leave'].with_user(self.user_hruser).create({
            'name':'Test',
            'holiday_status_id':self.leave_type.id,
            'department_id':self.employee_hruser.department_id.id,
            'employee_id':self.employee_hruser.id,
            'date_from':datetime.now(),
            'date_to':datetime.now()+relativedelta(days=1),
            'number_of_days':1,
        })
        withself.assertRaises(AccessError),self.cr.savepoint():
            other_leave.invalidate_cache(['name'])
            name=other_leave.with_user(self.user_employee_id).name

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_read_by_user_own(self):
        """Usersshouldbeabletoreadnamefieldofownrequests"""
        res=self.employee_leave.read(['name','number_of_days','state'])
        self.assertEqual(res[0]['name'],'Test')


@tests.tagged('access_rights','access_rights_write')
classTestAccessRightsWrite(TestHrHolidaysAccessRightsCommon):
    #base.group_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_update_by_user(self):
        """Usermayupdateitsleave"""
        self.employee_leave.with_user(self.user_employee_id).write({'name':'CrocodileDundeeismyman'})

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_update_by_user_other(self):
        """Usercannotupdateotherpeopleleaves"""
        other_leave=self.env['hr.leave'].with_user(self.user_hruser).create({
            'name':'Test',
            'holiday_status_id':self.leave_type.id,
            'department_id':self.employee_hruser.department_id.id,
            'employee_id':self.employee_hruser.id,
            'date_from':datetime.now(),
            'date_to':datetime.now()+relativedelta(days=1),
            'number_of_days':1,
        })
        withself.assertRaises(AccessError):
            other_leave.with_user(self.user_employee_id).write({'name':'CrocodileDundeeismyman'})

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_creation_for_other_user(self):
        """Employeecannotcreatesaleaverequestforanotheremployee"""
        HolidaysEmployeeGroup=self.env['hr.leave'].with_user(self.user_employee_id)
        withself.assertRaises(AccessError):
            HolidaysEmployeeGroup.create({
                'name':'Hol10',
                'employee_id':self.employee_hruser_id,
                'holiday_status_id':self.leave_type.id,
                'date_from':(datetime.today()-relativedelta(days=1)),
                'date_to':datetime.today(),
                'number_of_days':1,
            })

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_messaging_by_user(self):
        """Usermaycommunicateonitsownleaves,evenifvalidated"""
        self.employee_leave.with_user(self.user_employee_id).message_post(
            body='Ihazmessaging',
            subtype_xmlid='mail.mt_comment',
            message_type='comment'
        )

        self.employee_leave.with_user(self.user_hrmanager_id).action_approve()

        self.employee_leave.with_user(self.user_employee_id).message_post(
            body='Istillhazmessaging',
            subtype_xmlid='mail.mt_comment',
            message_type='comment'
        )

    #----------------------------------------
    #Validation:onevalidation,HR
    #----------------------------------------

    #base.group_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_hr_to_validate_by_user(self):
        """UsermaynotvalidateanyleavesinHRmode"""
        withself.assertRaises(UserError):
            self.employee_leave.with_user(self.user_employee_id).action_approve()

        withself.assertRaises(UserError):
            self.employee_leave.with_user(self.user_employee_id).write({'state':'validate'})

    #hr_holidays.group_hr_holidays_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_hr_to_validate_by_holiday_user(self):
        """ManagercanvalidateleavesinHRmode"""
        self.assertEqual(self.employee_leave.state,'confirm')
        self.employee_leave.with_user(self.user_hrmanager_id).action_approve()
        self.assertEqual(self.employee_leave.state,'validate')

    #hr_holidays.group_hr_holidays_manager

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_hr_to_validate_by_manager(self):
        """Managervalidateitsownleaves"""
        manager_leave=self.env['hr.leave'].with_user(self.user_hrmanager_id).create({
            'name':'Holmanager',
            'holiday_status_id':self.leave_type.id,
            'employee_id':self.employee_hrmanager_id,
            'date_from':(datetime.today()+relativedelta(days=15)),
            'date_to':(datetime.today()+relativedelta(days=16)),
            'number_of_days':1,
        })
        self.assertEqual(manager_leave.state,'confirm')
        manager_leave.action_approve()
        self.assertEqual(manager_leave.state,'validate')

    #----------------------------------------
    #Validation:onevalidation,manager
    #----------------------------------------

    #base.group_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_manager_to_validate_by_user(self):
        """Asimpleusercanvalidateinmanagermodeifheisleave_manager_id"""
        self.leave_type.write({'leave_validation_type':'manager'})
        values={
            'name':'HolHrUser',
            'employee_id':self.employee_hruser_id,
            'holiday_status_id':self.leave_type.id,
            'state':'confirm',
        }
        hr_leave=self.request_leave(self.user_hruser_id,datetime.now()+relativedelta(days=2),1,values)
        withself.assertRaises(AccessError):
            hr_leave.with_user(self.user_employee_id).action_approve()
        self.employee_hruser.write({'leave_manager_id':self.user_employee_id})
        hr_leave.with_user(self.user_employee_id).action_approve()

    #hr_holidays.group_hr_holidays_user

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_manager_to_validate_by_holiday_user(self):
        """Aholidayusercanvalidateinmanagermode"""
        self.leave_type.write({'leave_validation_type':'manager'})
        values={
            'name':'HolHrUser',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.leave_type.id,
            'state':'confirm',
        }
        hr_leave=self.request_leave(self.user_hruser_id,datetime.now()+relativedelta(days=2),1,values)
        hr_leave.with_user(self.user_hruser_id).action_approve()

    #----------------------------------------
    #Validation:double
    #----------------------------------------

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_double_validate(self):
        self.leave_type.write({'leave_validation_type':'both'})
        values={
            'name':'doubleHrManager',
            'employee_id':self.employee_hrmanager_id,
            'holiday_status_id':self.leave_type.id,
            'state':'confirm',
        }
        self.employee_hrmanager.leave_manager_id=self.env['res.users'].browse(1)
        hr_leave=self.request_leave(self.user_hruser_id,datetime.now()+relativedelta(days=6),1,values)

        withself.assertRaises(AccessError):
            hr_leave.with_user(self.user_employee_id).action_approve()

        self.employee_hrmanager.leave_manager_id=self.user_hruser
        hr_leave.with_user(self.user_hruser_id).action_approve()

        withself.assertRaises(AccessError):
            hr_leave.with_user(self.user_employee_id).action_validate()
        hr_leave.with_user(self.user_hruser_id).action_validate()

    #hr_holidays.group_hr_holidays_manager

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_double_validate_holiday_manager(self):
        self.leave_type.write({'leave_validation_type':'both'})
        values={
            'name':'doubleHrManager',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.leave_type.id,
            'state':'confirm',
        }
        hr_leave=self.request_leave(self.user_hrmanager_id,datetime.now()+relativedelta(days=4),1,values).with_user(self.user_hrmanager_id)
        hr_leave.action_approve()
        hr_leave.action_validate()

    #----------------------------------------
    #State=Refuse
    #----------------------------------------

    #base.group_user

    #hr_holidays.group_hr_holidays_user

    #TODOCanrefuse

    #hr_holidays.group_hr_holidays_manager

    #TODOCanrefuse

    #----------------------------------------
    #State=Cancel
    #----------------------------------------

    #base.group_user

    #TODOCanCancelifstart_dateinthefuture

    #hr_holidays.group_hr_holidays_user

    #TODOCanCancelifnotinvalidate

    #hr_holidays.group_hr_holidays_manager

    #TODOCanalwayscancelwithgreatpowerscomesgreatresponbilities


classTestMultiCompany(TestHrHolidaysCommon):

    defsetUp(self):
        super(TestMultiCompany,self).setUp()
        self.new_company=self.env['res.company'].create({
            'name':'CrocodileDundeeCompany',
        })
        self.leave_type=self.env['hr.leave.type'].create({
            'name':'Unlimited-CompanyNew',
            'company_id':self.new_company.id,
            'leave_validation_type':'hr',
            'allocation_type':'no',
        })
        self.rd_dept.manager_id=False
        self.hr_dept.manager_id=False

        self.employee_leave=self.env['hr.leave'].create({
            'name':'Test',
            'holiday_status_id':self.leave_type.id,
            'department_id':self.employee_emp.department_id.id,
            'employee_id':self.employee_emp.id,
            'date_from':datetime.now(),
            'date_to':datetime.now()+relativedelta(days=1),
            'number_of_days':1,
        })

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_access_other_company_user(self):
        employee_leave=self.employee_leave.with_user(self.user_employee)
        employee_leave.invalidate_cache(['name'])
        withself.assertRaises(AccessError):
            employee_leave.name

        withself.assertRaises(AccessError):
            employee_leave.action_approve()

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_access_other_company_officer(self):
        employee_leave_hruser=self.employee_leave.with_user(self.user_hruser)
        employee_leave_hruser.invalidate_cache(['name'])
        withself.assertRaises(AccessError):
            employee_leave_hruser.name

        withself.assertRaises(AccessError):
            employee_leave_hruser.action_approve()

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_access_other_company_manager(self):
        employee_leave_hrmanager=self.employee_leave.with_user(self.user_hrmanager)
        employee_leave_hrmanager.invalidate_cache(['name'])
        withself.assertRaises(AccessError):
            employee_leave_hrmanager.name

        withself.assertRaises(AccessError):
            employee_leave_hrmanager.action_approve()

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_access_no_company_user(self):
        self.leave_type.write({'company_id':False})
        employee_leave=self.employee_leave.with_user(self.user_employee)

        employee_leave.name
        withself.assertRaises(UserError):
            employee_leave.action_approve()
        self.assertEqual(employee_leave.state,'confirm')

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_access_no_company_officer(self):
        self.leave_type.write({'company_id':False})
        employee_leave_hruser=self.employee_leave.with_user(self.user_hruser)

        employee_leave_hruser.name
        employee_leave_hruser.action_approve()
        self.assertEqual(employee_leave_hruser.state,'validate')

    @mute_logger('flectra.models.unlink','flectra.addons.mail.models.mail_mail')
    deftest_leave_access_no_company_manager(self):
        self.leave_type.write({'company_id':False})
        employee_leave_hrmanager=self.employee_leave.with_user(self.user_hrmanager)

        employee_leave_hrmanager.name
        employee_leave_hrmanager.action_approve()
        self.assertEqual(employee_leave_hrmanager.state,'validate')
