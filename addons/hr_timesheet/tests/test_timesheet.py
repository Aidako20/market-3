#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase
fromflectra.exceptionsimportAccessError,UserError
fromflectra.testsimporttagged


classTestCommonTimesheet(TransactionCase):

    defsetUp(self):
        super(TestCommonTimesheet,self).setUp()

        #Crappyhacktodisabletherulefromtimesheetgrid,ifitexists
        #Theregistrydoesn'tcontainthefieldtimesheet_manager_id.
        #butthereisanir.ruleaboutit,crashingduringitsevaluation
        rule=self.env.ref('timesheet_grid.hr_timesheet_rule_approver_update',raise_if_not_found=False)
        ifrule:
            rule.active=False

        #customerpartner
        self.partner=self.env['res.partner'].create({
            'name':'CustomerTask',
            'email':'customer@task.com',
            'phone':'42',
        })

        self.analytic_account=self.env['account.analytic.account'].create({
            'name':'AnalyticAccountforTestCustomer',
            'partner_id':self.partner.id,
            'code':'TEST'
        })

        #projectandtasks
        self.project_customer=self.env['project.project'].create({
            'name':'ProjectX',
            'allow_timesheets':True,
            'partner_id':self.partner.id,
            'analytic_account_id':self.analytic_account.id,
        })
        self.task1=self.env['project.task'].create({
            'name':'TaskOne',
            'priority':'0',
            'kanban_state':'normal',
            'project_id':self.project_customer.id,
            'partner_id':self.partner.id,
        })
        self.task2=self.env['project.task'].create({
            'name':'TaskTwo',
            'priority':'1',
            'kanban_state':'done',
            'project_id':self.project_customer.id,
        })
        #users
        self.user_employee=self.env['res.users'].create({
            'name':'UserEmployee',
            'login':'user_employee',
            'email':'useremployee@test.com',
            'groups_id':[(6,0,[self.ref('hr_timesheet.group_hr_timesheet_user')])],
        })
        self.user_employee2=self.env['res.users'].create({
            'name':'UserEmployee2',
            'login':'user_employee2',
            'email':'useremployee2@test.com',
            'groups_id':[(6,0,[self.ref('hr_timesheet.group_hr_timesheet_user')])],
        })
        self.user_manager=self.env['res.users'].create({
            'name':'UserOfficer',
            'login':'user_manager',
            'email':'usermanager@test.com',
            'groups_id':[(6,0,[self.ref('hr_timesheet.group_timesheet_manager')])],
        })
        #employees
        self.empl_employee=self.env['hr.employee'].create({
            'name':'UserEmplEmployee',
            'user_id':self.user_employee.id,
        })
        self.empl_employee2=self.env['hr.employee'].create({
            'name':'UserEmplEmployee2',
            'user_id':self.user_employee2.id,
        })
        self.empl_manager=self.env['hr.employee'].create({
            'name':'UserEmplOfficer',
            'user_id':self.user_manager.id,
        })

@tagged('-at_install','post_install')
classTestTimesheet(TestCommonTimesheet):

    defsetUp(self):
        super(TestTimesheet,self).setUp()

        #Crappyhacktodisabletherulefromtimesheetgrid,ifitexists
        #Theregistrydoesn'tcontainthefieldtimesheet_manager_id.
        #butthereisanir.ruleaboutit,crashingduringitsevaluation
        rule=self.env.ref('timesheet_grid.timesheet_line_rule_user_update-unlink',raise_if_not_found=False)
        ifrule:
            rule.active=False

    deftest_log_timesheet(self):
        """Testwhenlogtimesheet:checkanalyticaccount,userandemployeearecorrectlyset."""
        Timesheet=self.env['account.analytic.line']
        timesheet_uom=self.project_customer.analytic_account_id.company_id.project_time_mode_id
        #employee1logsometimesheetontask1
        timesheet1=Timesheet.with_user(self.user_employee).create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'myfirsttimesheet',
            'unit_amount':4,
        })
        self.assertEqual(timesheet1.account_id,self.project_customer.analytic_account_id,'Analyticaccountshouldbethesameastheproject')
        self.assertEqual(timesheet1.employee_id,self.empl_employee,'Employeeshouldbetheoneofthecurrentuser')
        self.assertEqual(timesheet1.partner_id,self.task1.partner_id,'Customeroftaskshouldbethesameoftheonesetonnewtimesheet')
        self.assertEqual(timesheet1.product_uom_id,timesheet_uom,"TheUoMofthetimesheetshouldbetheonesetonthecompanyoftheanalyticaccount.")

        #employee1cannotlogtimesheetforemployee2
        withself.assertRaises(AccessError):
            timesheet2=Timesheet.with_user(self.user_employee).create({
                'project_id':self.project_customer.id,
                'task_id':self.task1.id,
                'name':'asecondtimesheetbutforemployee2',
                'unit_amount':3,
                'employee_id':self.empl_employee2.id,
            })

        #managerlogtimesheetforemployee2
        timesheet3=Timesheet.with_user(self.user_manager).create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'asecondtimesheetbutforemployee2',
            'unit_amount':7,
            'employee_id':self.empl_employee2.id,
        })
        self.assertEqual(timesheet3.user_id,self.user_employee2,'Timesheetusershouldbetheonelinkedtothegivenemployee')
        self.assertEqual(timesheet3.product_uom_id,timesheet_uom,"TheUoMofthetimesheet3shouldbetheonesetonthecompanyoftheanalyticaccount.")

        #employee1logsometimesheetonproject(notask)
        timesheet4=Timesheet.with_user(self.user_employee).create({
            'project_id':self.project_customer.id,
            'name':'myfirsttimesheet',
            'unit_amount':4,
        })
        self.assertEqual(timesheet4.partner_id,self.project_customer.partner_id,'Customerofnewtimesheetshouldbethesameoftheonesetproject(sincenotaskontimesheet)')

    deftest_log_access_rights(self):
        """Testaccessrights:usercanupdateitsowntimesheetsonly,andmanagercanchangeall"""
        #employee1logsometimesheetontask1
        Timesheet=self.env['account.analytic.line']
        timesheet1=Timesheet.with_user(self.user_employee).create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'myfirsttimesheet',
            'unit_amount':4,
        })
        #thenemployee2trytomodifyit
        withself.assertRaises(AccessError):
            timesheet1.with_user(self.user_employee2).write({
                'name':'itrytoupdatethistimesheet',
                'unit_amount':2,
            })
        #managercanmodifyalltimesheet
        timesheet1.with_user(self.user_manager).write({
            'unit_amount':8,
            'employee_id':self.empl_employee2.id,
        })
        self.assertEqual(timesheet1.user_id,self.user_employee2,'Changingtimesheetemployeeshouldchangetherelateduser')

    deftest_create_unlink_project(self):
        """Checkprojectcreation,andifnecessarytheanalyticaccountgeneratedwhenprojectshouldtracktime."""
        #createprojectwihtouttrackingtime,norprovideAA
        non_tracked_project=self.env['project.project'].create({
            'name':'Projectwithouttimesheet',
            'allow_timesheets':False,
            'partner_id':self.partner.id,
        })
        self.assertFalse(non_tracked_project.analytic_account_id,"Anontime-trackedprojectshouldn'tgenerateananalyticaccount")

        #createaprojecttrackingtime
        tracked_project=self.env['project.project'].create({
            'name':'Projectwithtimesheet',
            'allow_timesheets':True,
            'partner_id':self.partner.id,
        })
        self.assertTrue(tracked_project.analytic_account_id,"Atime-trackedprojectshouldgenerateananalyticaccount")
        self.assertTrue(tracked_project.analytic_account_id.active,"Atime-trackedprojectshouldgenerateanactiveanalyticaccount")
        self.assertEqual(tracked_project.partner_id,tracked_project.analytic_account_id.partner_id,"ThegeneratedAAshouldhavethesamepartnerastheproject")
        self.assertEqual(tracked_project.name,tracked_project.analytic_account_id.name,"ThegeneratedAAshouldhavethesamenameastheproject")
        self.assertEqual(tracked_project.analytic_account_id.project_count,1,"ThegeneratedAAshouldbelinkedtotheproject")

        #createaprojectwithouttrackingtime,butwithanalyticaccount
        analytic_project=self.env['project.project'].create({
            'name':'ProjectwithouttimesheetbutwithAA',
            'allow_timesheets':True,
            'partner_id':self.partner.id,
            'analytic_account_id':tracked_project.analytic_account_id.id,
        })
        self.assertNotEqual(analytic_project.name,tracked_project.analytic_account_id.name,"ThenameoftheassociatedAAcanbedifferentfromtheproject")
        self.assertEqual(tracked_project.analytic_account_id.project_count,2,"TheAAshouldbelinkedto2project")

        #analyticlinkedtoprojectscontainingtaskscannotberemoved
        task=self.env['project.task'].create({
            'name':'taskintrackedproject',
            'project_id':tracked_project.id,
        })
        withself.assertRaises(UserError):
            tracked_project.analytic_account_id.unlink()

        #taskcanberemoved,asthereisnotimesheet
        task.unlink()

        #sincebothprojectslinkedtothesameanalyticaccountareempty(notask),itcanberemoved
        tracked_project.analytic_account_id.unlink()

    deftest_transfert_project(self):
        """Transferttaskwithtimesheettoanotherproject."""
        Timesheet=self.env['account.analytic.line']
        #createasecondproject
        self.project_customer2=self.env['project.project'].create({
            'name':'ProjectNUMBERDEUX',
            'allow_timesheets':True,
        })
        #employee1logsometimesheetontask1
        Timesheet.create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'myfirsttimesheet',
            'unit_amount':4,
        })

        timesheet_count1=Timesheet.search_count([('project_id','=',self.project_customer.id)])
        timesheet_count2=Timesheet.search_count([('project_id','=',self.project_customer2.id)])
        self.assertEqual(timesheet_count1,1,"Onetimesheetinproject1")
        self.assertEqual(timesheet_count2,0,"Notimesheetinproject2")
        self.assertEqual(len(self.task1.timesheet_ids),1,"Thetimesheetshouldbelinkedtotask1")

        #changeprojectoftask1
        self.task1.write({
            'project_id':self.project_customer2.id
        })

        timesheet_count1=Timesheet.search_count([('project_id','=',self.project_customer.id)])
        timesheet_count2=Timesheet.search_count([('project_id','=',self.project_customer2.id)])
        self.assertEqual(timesheet_count1,0,"Notimesheetinproject1")
        self.assertEqual(timesheet_count2,1,"Stillonetimesheetinproject2")
        self.assertEqual(len(self.task1.timesheet_ids),1,"Thetimesheetstillshouldbelinkedtotask1")

        #itisforbiddentosetataskwithtimesheetwithoutproject
        withself.assertRaises(UserError):
            self.task1.write({
                'project_id':False
            })

    deftest_recompute_amount_for_multiple_timesheets(self):
        """Checkthatamountisrecomputedcorrectlywhensettingunit_amountformultipletimesheetsatonce."""
        Timesheet=self.env['account.analytic.line']
        self.empl_employee.timesheet_cost=5.0
        self.empl_employee2.timesheet_cost=6.0
        #createatimesheetforeachemployee
        timesheet_1=Timesheet.with_user(self.user_employee).create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'/',
            'unit_amount':1,
        })
        timesheet_2=Timesheet.with_user(self.user_employee2).create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'/',
            'unit_amount':1,
        })
        timesheets=timesheet_1+timesheet_2

        withself.assertRaises(AccessError):
            #shouldraisesinceemployee1doesn'thavetheaccessrightstoupdateemployee's2timesheet
            timesheets.with_user(self.empl_employee.user_id).write({
                'unit_amount':2,
            })

        timesheets.with_user(self.user_manager).write({
            'unit_amount':2,
        })

        #sincetimesheetcostsaredifferentforbothemployees,weshouldgetdifferentamounts
        self.assertRecordValues(timesheets.with_user(self.user_manager),[{
            'amount':-10.0,
        },{
            'amount':-12.0,
        }])

    deftest_recompute_partner_from_task_customer_change(self):
        partner2=self.env['res.partner'].create({
            'name':'CustomerTask2',
            'email':'customer2@task.com',
            'phone':'43',
        })

        timesheet_entry=self.env['account.analytic.line'].create({
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'myonlytimesheet',
            'unit_amount':4,
        })

        self.assertEqual(timesheet_entry.partner_id,self.partner,"Thetimesheetentry'spartnershouldbeequaltothetask'spartner/customer")

        self.task1.write({'partner_id':partner2})

        self.assertEqual(timesheet_entry.partner_id,partner2,"Thetimesheetentry'spartnershouldstillbeequaltothetask'spartner/customer,afterthechange")

    deftest_add_time_from_wizard(self):
        config=self.env["res.config.settings"].create({
                "timesheet_min_duration":60,
                "timesheet_rounding":15,
            })
        config.execute()
        wizard_min=self.env['project.task.create.timesheet'].create({
                'time_spent':0.7,
                'task_id':self.task1.id,
            })
        wizard_round=self.env['project.task.create.timesheet'].create({
                'time_spent':1.15,
                'task_id':self.task1.id,
            })
        self.assertEqual(wizard_min.save_timesheet().unit_amount,1,"Thetimesheet'sdurationshouldbe1h(MinimumDuration=60').")
        self.assertEqual(wizard_round.save_timesheet().unit_amount,1.25,"Thetimesheet'sdurationshouldbe1h15(Rounding=15').")

    deftest_task_with_timesheet_project_change(self):
        '''Thistestchecksthatnoerrorisraisedwhenmovingataskthatcontainstimesheettoanotherproject.
           Thismoveimplyingwritingontheaccount.analytic.line.
        '''

        project_manager=self.env['res.users'].create({
            'name':'user_project_manager',
            'login':'user_project_manager',
            'groups_id':[(6,0,[self.ref('project.group_project_manager')])],
        })

        project=self.env['project.project'].create({
            'name':'ProjectWithTimesheets',
            'privacy_visibility':'employees',
            'allow_timesheets':True,
            'user_id':project_manager.id,
        })
        second_project=self.env['project.project'].create({
            'name':'Projectw/timesheets',
            'privacy_visibility':'employees',
            'allow_timesheets':True,
            'user_id':project_manager.id,
        })

        task_1=self.env['project.task'].create({
            'name':'Firsttask',
            'user_id':self.user_employee2.id,
            'project_id':project.id
        })

        timesheet=self.env['account.analytic.line'].create({
            'name':'FirstTimeSheet',
            'project_id':project.id,
            'task_id':task_1.id,
            'unit_amount':2,
            'employee_id':self.empl_employee2.id
        })

        task_1.with_user(project_manager).write({
            'project_id':second_project.id
        })

        self.assertEqual(timesheet.project_id,second_project,'Theproject_idoftimesheetshouldbesecond_project')

    deftest_ensure_product_uom_set_in_timesheet(self):
        self.assertFalse(self.project_customer.timesheet_ids,'Notimesheetshouldberecordedinthisproject')
        self.assertFalse(self.project_customer.total_timesheet_time,'Thetotaltimerecordedshouldbeequalto0sincenotimesheetisrecorded.')

        timesheet1,timesheet2=self.env['account.analytic.line'].create([
            {'unit_amount':1.0,'project_id':self.project_customer.id},
            {'unit_amount':3.0,'project_id':self.project_customer.id,'product_uom_id':False},
        ])
        self.assertEqual(
            timesheet1.product_uom_id,
            self.project_customer.analytic_account_id.company_id.timesheet_encode_uom_id,
            'ThedefaultUoMsetonthetimesheetshouldbetheonesetonthecompanyofAA.'
        )
        self.assertEqual(
            timesheet2.product_uom_id,
            self.project_customer.analytic_account_id.company_id.timesheet_encode_uom_id,
            'Eveniftheproduct_uom_idfieldisemptyinthevals,theproduct_uom_idshouldhaveaUoMbydefault,'
            'otherwisethe`total_timesheet_time`inprojectshouldnotincludedthetimesheet.'
        )
        self.assertEqual(self.project_customer.timesheet_ids,timesheet1+timesheet2)
        self.assertEqual(
            self.project_customer.total_timesheet_time,
            timesheet1.unit_amount+timesheet2.unit_amount,
            'Thetotaltimesheettimeofthisprojectshouldbeequalto4.'
        )

    deftest_create_timesheet_employee_not_in_company(self):
        '''ts.employee_idonlyiftheuserhasanemployeeinthecompanyoroneemployeeforallcompanies.
        '''
        company_2=self.env['res.company'].create({'name':'Company2'})
        company_3=self.env['res.company'].create({'name':'Company3'})

        analytic_account=self.env['account.analytic.account'].create({
            'name':'AaAa',
            'company_id':company_3.id,
        })
        project=self.env['project.project'].create({
            'name':'AaProject',
            'company_id':company_3.id,
            'analytic_account_id':analytic_account.id,
        })
        task=self.env['project.task'].create({
            'name':'AaTask',
            'project_id':project.id,
        })

        Timesheet=self.env['account.analytic.line'].with_context(allowed_company_ids=[company_3.id,company_2.id,self.env.company.id])
        timesheet=Timesheet.create({
            'name':'Timesheet',
            'project_id':project.id,
            'task_id':task.id,
            'unit_amount':2,
            'user_id':self.user_manager.id,
            'company_id':company_3.id,
        })
        self.assertEqual(timesheet.employee_id,self.user_manager.employee_id,'Asthereisauniqueemployeeforthisuser,itmustbefound')

        self.env['hr.employee'].with_company(company_2).create({
            'name':'Employee2',
            'user_id':self.user_manager.id,
        })
        timesheet=Timesheet.create({
            'name':'Timesheet',
            'project_id':project.id,
            'task_id':task.id,
            'unit_amount':2,
            'user_id':self.user_manager.id,
            'company_id':company_3.id,
        })
        self.assertFalse(timesheet.employee_id,'Asthereareseveralemployeesforthisuser,butnoneoftheminthiscompany,nonemustbefound')

    deftest_create_timesheet_with_archived_employee(self):
        '''thetimesheetcanbecreatedoreditedonlywithanactiveemployee
        '''
        self.empl_employee2.active=False
        batch_vals={
            'project_id':self.project_customer.id,
            'task_id':self.task1.id,
            'name':'archivedemployeetimesheet',
            'unit_amount':3,
            'employee_id':self.empl_employee2.id
        }

        self.assertRaises(UserError,self.env['account.analytic.line'].create,batch_vals)

        batch_vals["employee_id"]=self.empl_employee.id
        timesheet=self.env['account.analytic.line'].create(batch_vals)

        withself.assertRaises(UserError):
            timesheet.employee_id=self.empl_employee2

    deftest_check_timesheet_user(self):
        """TestCheckwhetherthetimesheetuseriscorrectornot.

            Part1:TestCase:
            ----------
                1)Createemployeewithoutuser
                2)Createtimesheet
                3)Checktheuserofthetimesheet

            Part2: TestCase:
            ----------
                3)Createatimesheetoftheemployeelinkedtotheuser
                4)Checktheuserofthetimesheet
        """

        Timesheet=self.env['account.analytic.line']

        emp_without_user=self.env['hr.employee'].create({
            'name':'EmplEmployee',
        })
        without_user_timesheet=Timesheet.with_context(default_employee_id=emp_without_user.id).create({
            'project_id':self.project_customer.id,
            'unit_amount':8.0,
        })
        self.assertFalse(without_user_timesheet.user_id,'Userisnotsetintimesheet.')

        with_user_timesheet=Timesheet.with_context(default_employee_id=self.empl_employee.id).create({
            'project_id':self.project_customer.id,
            'unit_amount':8.0,
        })
        self.assertEqual(with_user_timesheet.user_id,self.user_employee,'UserEmployeeissetintimesheet.')

    deftest_create_timesheet_with_companyless_analytic_account(self):
        """Thistestensuresthatatimesheetcanbecreatedonananalyticaccountwhosecompany_idissettoFalse"""
        self.project_customer.analytic_account_id.company_id=False
        timesheet=self.env['account.analytic.line'].with_user(self.user_employee).create(
            {'unit_amount':1.0,'project_id':self.project_customer.id})
        self.assertEqual(timesheet.product_uom_id,self.project_customer.company_id.project_time_mode_id,
                         "Theproduct_uom_idofthetimesheetshouldbeequaltotheproject'scompanyuom"
                         "iftheproject'sanalyticaccounthasnocompany_id")

    deftest_percentage_of_planned_hours(self):
        """Testthepercentageofplannedhoursonatask."""
        self.task1.planned_hours=round(11/60,2)
        self.assertEqual(self.task1.effective_hours,0,'Notimesheetshouldbecreatedyet.')
        self.assertEqual(self.task1.progress,0,'Notimesheetshouldbecreatedyet.')
        self.env['account.analytic.line'].create([
            {
                'name':'Timesheet',
                'project_id':self.project_customer.id,
                'task_id':self.task1.id,
                'unit_amount':3/60,
                'employee_id':self.empl_employee.id,
            },{
                'name':'Timesheet',
                'project_id':self.project_customer.id,
                'task_id':self.task1.id,
                'unit_amount':4/60,
                'employee_id':self.empl_employee.id,
            },{
                'name':'Timesheet',
                'project_id':self.project_customer.id,
                'task_id':self.task1.id,
                'unit_amount':4/60,
                'employee_id':self.empl_employee.id,
            },
        ])
        self.assertEqual(self.task1.progress,100,'Thepercentageofplannedhoursshouldbe100%.')
