#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime
fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta
frompsycopg2importIntegrityError

fromflectraimportfields
fromflectra.exceptionsimportAccessError,ValidationError,UserError
fromflectra.toolsimportmute_logger,test_reports

fromflectra.addons.hr_holidays.tests.commonimportTestHrHolidaysCommon


classTestHolidaysFlow(TestHrHolidaysCommon):

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_00_leave_request_flow_unlimited(self):
        """Testingleaverequestflow:unlimitedtypeofleaverequest"""
        Requests=self.env['hr.leave']
        HolidaysStatus=self.env['hr.leave.type']

        #HrManagercreatessomeholidaystatuses
        HolidayStatusManagerGroup=HolidaysStatus.with_user(self.user_hrmanager_id)
        HolidayStatusManagerGroup.create({
            'name':'WithMeetingType',
            'allocation_type':'no',
        })
        self.holidays_status_hr=HolidayStatusManagerGroup.create({
            'name':'NotLimitedHR',
            'allocation_type':'no',
            'leave_validation_type':'hr',
            'validity_start':False,
        })
        self.holidays_status_manager=HolidayStatusManagerGroup.create({
            'name':'NotLimitedManager',
            'allocation_type':'no',
            'leave_validation_type':'manager',
            'validity_start':False,
        })

        HolidaysEmployeeGroup=Requests.with_user(self.user_employee_id)

        #Employeecreatesaleaverequestinano-limitcategoryhrmanageronly
        hol1_employee_group=HolidaysEmployeeGroup.create({
            'name':'Hol11',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_status_hr.id,
            'date_from':(datetime.today()-relativedelta(days=1)),
            'date_to':datetime.today(),
            'number_of_days':1,
        })
        hol1_user_group=hol1_employee_group.with_user(self.user_hruser_id)
        hol1_manager_group=hol1_employee_group.with_user(self.user_hrmanager_id)
        self.assertEqual(hol1_user_group.state,'confirm','hr_holidays:newlycreatedleaverequestshouldbeinconfirmstate')

        #HrUservalidatestheemployeeleaverequest->shouldwork
        hol1_user_group.action_approve()
        self.assertEqual(hol1_manager_group.state,'validate','hr_holidays:validatedleaverequestshouldbeinvalidatestate')

        #Employeecreatesaleaverequestinano-limitcategorydepartmentmanageronly
        hol12_employee_group=HolidaysEmployeeGroup.create({
            'name':'Hol12',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_status_manager.id,
            'date_from':(datetime.today()+relativedelta(days=12)),
            'date_to':(datetime.today()+relativedelta(days=13)),
            'number_of_days':1,
        })
        hol12_user_group=hol12_employee_group.with_user(self.user_hruser_id)
        hol12_manager_group=hol12_employee_group.with_user(self.user_hrmanager_id)
        self.assertEqual(hol12_user_group.state,'confirm','hr_holidays:newlycreatedleaverequestshouldbeinconfirmstate')

        #HrManagervalidatetheemployeeleaverequest
        hol12_manager_group.action_approve()
        self.assertEqual(hol1_user_group.state,'validate','hr_holidays:validatesleaverequestshouldbeinvalidatestate')


    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_01_leave_request_flow_limited(self):
        """Testingleaverequestflow:limitedtypeofleaverequest"""
        Requests=self.env['hr.leave']
        Allocations=self.env['hr.leave.allocation']
        HolidaysStatus=self.env['hr.leave.type']

        holiday_status_paid_time_off=self.env['hr.leave.type'].create({
            'name':'PaidTimeOff',
            'allocation_type':'fixed',
            'leave_validation_type':'both',
            'validity_start':time.strftime('%Y-%m-01'),
            'responsible_id':self.env.ref('base.user_admin').id,
        })

        self.env['hr.leave.allocation'].create([
            {
                'name':'PaidTimeoffforDavid',
                'holiday_status_id':holiday_status_paid_time_off.id,
                'number_of_days':20,
                'employee_id':self.employee_emp_id,
                'state':'validate',
            },{
                'name':'PaidTimeoffforDavid',
                'holiday_status_id':holiday_status_paid_time_off.id,
                'number_of_days':20,
                'employee_id':self.ref('hr.employee_admin'),
                'state':'validate',
            }
        ])

        def_check_holidays_status(holiday_status,ml,lt,rl,vrl):
            self.assertEqual(holiday_status.max_leaves,ml,
                             'hr_holidays:wrongtypedayscomputation')
            self.assertEqual(holiday_status.leaves_taken,lt,
                             'hr_holidays:wrongtypedayscomputation')
            self.assertEqual(holiday_status.remaining_leaves,rl,
                             'hr_holidays:wrongtypedayscomputation')
            self.assertEqual(holiday_status.virtual_remaining_leaves,vrl,
                             'hr_holidays:wrongtypedayscomputation')

        #HrManagercreatessomeholidaystatuses
        HolidayStatusManagerGroup=HolidaysStatus.with_user(self.user_hrmanager_id)
        HolidayStatusManagerGroup.create({
            'name':'WithMeetingType',
            'allocation_type':'no',
            'validity_start':False,
        })

        self.holidays_status_limited=HolidayStatusManagerGroup.create({
            'name':'Limited',
            'allocation_type':'fixed',
            'allocation_validation_type':'both',
            'leave_validation_type':'both',
            'validity_start':False,
        })
        HolidaysEmployeeGroup=Requests.with_user(self.user_employee_id)

        #HrUserallocatessomeleavestotheemployee
        aloc1_user_group=Allocations.with_user(self.user_hruser_id).create({
            'name':'Daysforlimitedcategory',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_status_limited.id,
            'number_of_days':2,
        })
        #HrUservalidatesthefirststep
        aloc1_user_group.action_approve()

        #HrManagervalidatesthesecondstep
        aloc1_user_group.with_user(self.user_hrmanager_id).action_validate()
        #ChecksEmployeehaseffectivelysomedaysleft
        hol_status_2_employee_group=self.holidays_status_limited.with_user(self.user_employee_id)
        _check_holidays_status(hol_status_2_employee_group,2.0,0.0,2.0,2.0)

        #Employeecreatesaleaverequestinthelimitedcategory,nowthathehassomedaysleft
        hol2=HolidaysEmployeeGroup.create({
            'name':'Hol22',
            'employee_id':self.employee_emp_id,
            'holiday_status_id':self.holidays_status_limited.id,
            'date_from':(datetime.today()+relativedelta(days=2)).strftime('%Y-%m-%d%H:%M'),
            'date_to':(datetime.today()+relativedelta(days=3)),
            'number_of_days':1,
        })
        hol2_user_group=hol2.with_user(self.user_hruser_id)
        #Checkleftdays:-1virtualremainingday
        hol_status_2_employee_group.invalidate_cache()
        _check_holidays_status(hol_status_2_employee_group,2.0,0.0,2.0,1.0)

        #HrManagervalidatesthefirststep
        hol2_user_group.with_user(self.user_hrmanager_id).action_approve()
        self.assertEqual(hol2.state,'validate1',
                         'hr_holidays:firstvalidationshouldleadtovalidate1state')

        #HrManagervalidatesthesecondstep
        hol2_user_group.with_user(self.user_hrmanager_id).action_validate()
        self.assertEqual(hol2.state,'validate',
                         'hr_holidays:secondvalidationshouldleadtovalidatestate')
        #Checkleftdays:-1daytaken
        _check_holidays_status(hol_status_2_employee_group,2.0,1.0,1.0,1.0)

        #HrManagerfindsanerror:herefusestheleaverequest
        hol2.with_user(self.user_hrmanager_id).action_refuse()
        self.assertEqual(hol2.state,'refuse',
                         'hr_holidays:refuseshouldleadtorefusestate')
        #Checkleftdays:2daysleftagain

        hol_status_2_employee_group.invalidate_cache(['max_leaves'])
        _check_holidays_status(hol_status_2_employee_group,2.0,0.0,2.0,2.0)

        self.assertEqual(hol2.state,'refuse',
                         'hr_holidays:hr_usershouldnotbeabletoresetarefusedleaverequest')

        #HrManagerresetstherequest
        hol2_manager_group=hol2.with_user(self.user_hrmanager_id)
        hol2_manager_group.action_draft()
        self.assertEqual(hol2.state,'draft',
                         'hr_holidays:resettingshouldleadtodraftstate')

        employee_id=self.ref('hr.employee_admin')
        #clcanbeofmaximum20daysforemployee_admin
        hol3_status=holiday_status_paid_time_off.with_context(employee_id=employee_id)
        #Iassignthedatesintheholidayrequestfor1day
        hol3=Requests.create({
            'name':'SickTimeOff',
            'holiday_status_id':hol3_status.id,
            'date_from':datetime.today().strftime('%Y-%m-1010:00:00'),
            'date_to':datetime.today().strftime('%Y-%m-1119:00:00'),
            'employee_id':employee_id,
            'number_of_days':1,
        })
        #IfindasmallmistakeonmyleaverequesttoIclickon"Refuse"buttontocorrectamistake.
        hol3.action_refuse()
        self.assertEqual(hol3.state,'refuse','hr_holidays:refuseshouldleadtorefusestate')
        #Iagainsettodraftandthenconfirm.
        hol3.action_draft()
        self.assertEqual(hol3.state,'draft','hr_holidays:resettingshouldleadtodraftstate')
        hol3.action_confirm()
        self.assertEqual(hol3.state,'confirm','hr_holidays:confirmingshouldleadtoconfirmstate')
        #Ivalidatetheholidayrequestbyclickingon"ToApprove"button.
        hol3.action_approve()
        hol3.action_validate()
        self.assertEqual(hol3.state,'validate','hr_holidays:validationshouldleadtovalidatestate')
        #Checkleftdaysforcasualleave:19daysleft
        _check_holidays_status(hol3_status,20.0,1.0,19.0,19.0)

    deftest_10_leave_summary_reports(self):
        #PrinttheHRHolidays(SummaryEmployee)Reportthroughthewizard
        ctx={
            'model':'hr.employee',
            'active_ids':[self.ref('hr.employee_admin')]
        }
        data_dict={
            'date_from':datetime.today().strftime('%Y-%m-01'),
            'emp':[(6,0,[self.ref('hr.employee_admin')])],
            'holiday_type':'Approved'
        }
        self.env.company.external_report_layout_id=self.env.ref('web.external_layout_standard').id
        test_reports.try_report_action(self.env.cr,self.env.uid,'action_hr_holidays_summary_employee',wiz_data=data_dict,context=ctx,our_module='hr_holidays')

    deftest_sql_constraint_dates(self):
        #Thegoalismainlytoverifythatahumanfriendly
        #errormessageistriggeredifthedate_fromisafter
        #date_to.ComingfromabugduetothenewORM13.0

        holiday_status_paid_time_off=self.env['hr.leave.type'].create({
            'name':'PaidTimeOff',
            'allocation_type':'fixed',
            'leave_validation_type':'both',
            'validity_start':time.strftime('%Y-%m-01'),
            'responsible_id':self.env.ref('base.user_admin').id,
        })

        self.env['hr.leave.allocation'].create({
            'name':'PaidTimeoffforDavid',
            'holiday_status_id':holiday_status_paid_time_off.id,
            'number_of_days':20,
            'employee_id':self.ref('hr.employee_admin'),
            'state':'validate',
        })

        leave_vals={
            'name':'SickTimeOff',
            'holiday_status_id':holiday_status_paid_time_off.id,
            'date_from':datetime.today().strftime('%Y-%m-1119:00:00'),
            'date_to':datetime.today().strftime('%Y-%m-1010:00:00'),
            'employee_id':self.ref('hr.employee_admin'),
            'number_of_days':1,
        }
        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError):
                withself.cr.savepoint():
                    self.env['hr.leave'].create(leave_vals)

        leave_vals={
            'name':'SickTimeOff',
            'holiday_status_id':holiday_status_paid_time_off.id,
            'date_from':datetime.today().strftime('%Y-%m-1010:00:00'),
            'date_to':datetime.today().strftime('%Y-%m-1119:00:00'),
            'employee_id':self.ref('hr.employee_admin'),
            'number_of_days':1,
        }
        leave=self.env['hr.leave'].create(leave_vals)
        withmute_logger('flectra.sql_db'):
            withself.assertRaises(IntegrityError): #NoValidationError
                withself.cr.savepoint():
                    leave.write({
                        'date_from':datetime.today().strftime('%Y-%m-1119:00:00'),
                        'date_to':datetime.today().strftime('%Y-%m-1010:00:00'),
                    })
