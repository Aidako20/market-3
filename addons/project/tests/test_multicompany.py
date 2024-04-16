#-*-coding:utf-8-*-

fromcontextlibimportcontextmanager

fromflectra.tests.commonimportSavepointCase,Form
fromflectra.exceptionsimportAccessError,UserError


classTestMultiCompanyCommon(SavepointCase):

    @classmethod
    defsetUpMultiCompany(cls):

        #createcompanies
        cls.company_a=cls.env['res.company'].create({
            'name':'CompanyA'
        })
        cls.company_b=cls.env['res.company'].create({
            'name':'CompanyB'
        })

        #sharedcustomers
        cls.partner_1=cls.env['res.partner'].create({
            'name':'ValidLelitre',
            'email':'valid.lelitre@agrolait.com',
            'company_id':False,
        })
        cls.partner_2=cls.env['res.partner'].create({
            'name':'ValidPoilvache',
            'email':'valid.other@gmail.com',
            'company_id':False,
        })

        #userstousethroughthevarioustests
        user_group_employee=cls.env.ref('base.group_user')
        Users=cls.env['res.users'].with_context({'no_reset_password':True})

        cls.user_employee_company_a=Users.create({
            'name':'EmployeeCompanyA',
            'login':'employee-a',
            'email':'employee@companya.com',
            'company_id':cls.company_a.id,
            'company_ids':[(6,0,[cls.company_a.id])],
            'groups_id':[(6,0,[user_group_employee.id])]
        })
        cls.user_manager_company_a=Users.create({
            'name':'ManagerCompanyA',
            'login':'manager-a',
            'email':'manager@companya.com',
            'company_id':cls.company_a.id,
            'company_ids':[(6,0,[cls.company_a.id])],
            'groups_id':[(6,0,[user_group_employee.id])]
        })
        cls.user_employee_company_b=Users.create({
            'name':'EmployeeCompanyB',
            'login':'employee-b',
            'email':'employee@companyb.com',
            'company_id':cls.company_b.id,
            'company_ids':[(6,0,[cls.company_b.id])],
            'groups_id':[(6,0,[user_group_employee.id])]
        })
        cls.user_manager_company_b=Users.create({
            'name':'ManagerCompanyB',
            'login':'manager-b',
            'email':'manager@companyb.com',
            'company_id':cls.company_b.id,
            'company_ids':[(6,0,[cls.company_b.id])],
            'groups_id':[(6,0,[user_group_employee.id])]
        })

    @contextmanager
    defsudo(self,login):
        old_uid=self.uid
        try:
            user=self.env['res.users'].sudo().search([('login','=',login)])
            #switchuser
            self.uid=user.id
            self.env=self.env(user=self.uid)
            yield
        finally:
            #back
            self.uid=old_uid
            self.env=self.env(user=self.uid)

    @contextmanager
    defallow_companies(self,company_ids):
        """Thecurrentuserwillbeallowedineachgivencompanies(likehecanseesalloftheminthecompanyswitcherandtheyareallchecked)"""
        old_allow_company_ids=self.env.user.company_ids.ids
        current_user=self.env.user
        try:
            current_user.write({'company_ids':company_ids})
            context=dict(self.env.context,allowed_company_ids=company_ids)
            self.env=self.env(user=current_user,context=context)
            yield
        finally:
            #back
            current_user.write({'company_ids':old_allow_company_ids})
            context=dict(self.env.context,allowed_company_ids=old_allow_company_ids)
            self.env=self.env(user=current_user,context=context)

    @contextmanager
    defswitch_company(self,company):
        """Changethecompanyinwhichthecurrentuserislogged"""
        old_companies=self.env.context.get('allowed_company_ids',[])
        try:
            #switchcompanyincontext
            new_companies=list(old_companies)
            ifcompany.idnotinnew_companies:
                new_companies=[company.id]+new_companies
            else:
                new_companies.insert(0,new_companies.pop(new_companies.index(company.id)))
            context=dict(self.env.context,allowed_company_ids=new_companies)
            self.env=self.env(context=context)
            yield
        finally:
            #back
            context=dict(self.env.context,allowed_company_ids=old_companies)
            self.env=self.env(context=context)


classTestMultiCompanyProject(TestMultiCompanyCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMultiCompanyProject,cls).setUpClass()

        cls.setUpMultiCompany()

        user_group_project_user=cls.env.ref('project.group_project_user')
        user_group_project_manager=cls.env.ref('project.group_project_manager')

        #setupusers
        cls.user_employee_company_a.write({
            'groups_id':[(4,user_group_project_user.id)]
        })
        cls.user_manager_company_a.write({
            'groups_id':[(4,user_group_project_manager.id)]
        })
        cls.user_employee_company_b.write({
            'groups_id':[(4,user_group_project_user.id)]
        })
        cls.user_manager_company_b.write({
            'groups_id':[(4,user_group_project_manager.id)]
        })

        #createprojectinbothcompanies
        Project=cls.env['project.project'].with_context({'mail_create_nolog':True,'tracking_disable':True})
        cls.project_company_a=Project.create({
            'name':'ProjectCompanyA',
            'alias_name':'project+companya',
            'partner_id':cls.partner_1.id,
            'company_id':cls.company_a.id,
            'type_ids':[
                (0,0,{
                    'name':'New',
                    'sequence':1,
                }),
                (0,0,{
                    'name':'Won',
                    'sequence':10,
                })
            ]
        })
        cls.project_company_b=Project.create({
            'name':'ProjectCompanyB',
            'alias_name':'project+companyb',
            'partner_id':cls.partner_1.id,
            'company_id':cls.company_b.id,
            'type_ids':[
                (0,0,{
                    'name':'New',
                    'sequence':1,
                }),
                (0,0,{
                    'name':'Won',
                    'sequence':10,
                })
            ]
        })
        #already-existingtasksincompanyAandB
        Task=cls.env['project.task'].with_context({'mail_create_nolog':True,'tracking_disable':True})
        cls.task_1=Task.create({
            'name':'Task1inProjectA',
            'user_id':cls.user_employee_company_a.id,
            'project_id':cls.project_company_a.id
        })
        cls.task_2=Task.create({
            'name':'Task2inProjectB',
            'user_id':cls.user_employee_company_b.id,
            'project_id':cls.project_company_b.id
        })

    deftest_create_project(self):
        """Checkprojectcreationinmultiplecompanies"""
        withself.sudo('manager-a'):
            project=self.env['project.project'].with_context({'tracking_disable':True}).create({
                'name':'ProjectCompanyA',
                'partner_id':self.partner_1.id,
            })
            self.assertEqual(project.company_id,self.env.user.company_id,"Anewlycreatedprojectshouldbeinthecurrentusercompany")

            withself.switch_company(self.company_b):
                withself.assertRaises(AccessError,msg="Managercannotcreateprojectinacompanyinwhichheisnotallowed"):
                    project=self.env['project.project'].with_context({'tracking_disable':True}).create({
                        'name':'ProjectCompanyB',
                        'partner_id':self.partner_1.id,
                        'company_id':self.company_b.id
                    })

                #whenallowedinothercompany,cancreateaprojectinanothercompany(differentfromtheoneinwhichyouarelogged)
                withself.allow_companies([self.company_a.id,self.company_b.id]):
                    project=self.env['project.project'].with_context({'tracking_disable':True}).create({
                        'name':'ProjectCompanyB',
                        'partner_id':self.partner_1.id,
                        'company_id':self.company_b.id
                    })

    deftest_generate_analytic_account(self):
        """Checktheanalyticaccountgeneration,companypropagation"""
        withself.sudo('manager-b'):
            withself.allow_companies([self.company_a.id,self.company_b.id]):
                self.project_company_a._create_analytic_account()

                self.assertEqual(self.project_company_a.company_id,self.project_company_a.analytic_account_id.company_id,"Theanalyticaccountcreatedfromaprojectshouldbeinthesamecompany")

    deftest_create_task(self):
        withself.sudo('employee-a'):
            #createtask,setproject;theonchangewillsetthecorrectcompany
            withForm(self.env['project.task'].with_context({'tracking_disable':True}))astask_form:
                task_form.name='TestTaskincompanyA'
                task_form.project_id=self.project_company_a
            task=task_form.save()

            self.assertEqual(task.company_id,self.project_company_a.company_id,"Thecompanyofthetaskshouldbetheonefromitsproject.")

    deftest_move_task(self):
        withself.sudo('employee-a'):
            withself.allow_companies([self.company_a.id,self.company_b.id]):
                withForm(self.task_1)astask_form:
                    task_form.project_id=self.project_company_b
                task=task_form.save()

                self.assertEqual(task.company_id,self.company_b,"Thecompanyofthetaskshouldbetheonefromitsproject.")

                withForm(self.task_1)astask_form:
                    task_form.project_id=self.project_company_a
                task=task_form.save()

                self.assertEqual(task.company_id,self.company_a,"Movingataskshouldchangeitscompany.")

    deftest_create_subtask(self):
        withself.sudo('employee-a'):
            withself.allow_companies([self.company_a.id,self.company_b.id]):
                #createsubtask,setparent;theonchangewillsetthecorrectcompanyandsubtaskproject
                withForm(self.env['project.task'].with_context({'tracking_disable':True}))astask_form:
                    task_form.name='TestSubtaskincompanyB'
                    task_form.parent_id=self.task_1
                    task_form.project_id=self.project_company_b

                task=task_form.save()

                self.assertEqual(task.company_id,self.project_company_b.company_id,"Thecompanyofthesubtaskshouldbetheonefromitsproject,andnotfromitsparent.")

                #setparentonexistingorphantask;theonchangewillsetthecorrectcompanyandsubtaskproject
                self.task_2.write({'project_id':False})
                withForm(self.task_2)astask_form:
                    task_form.name='TestTask2becomeschildofTask1(othercompany)'
                    task_form.parent_id=self.task_1
                task=task_form.save()

                self.assertEqual(task.company_id,task.project_id.company_id,"Thecompanyoftheorphansubtaskshouldbetheonefromitsproject.")

    deftest_cross_subtask_project(self):
        #setupdefaultsubtaskproject
        self.project_company_a.write({'allow_subtasks':True,'subtask_project_id':self.project_company_b.id})

        withself.sudo('employee-a'):
            withself.allow_companies([self.company_a.id,self.company_b.id]):
                withForm(self.env['project.task'].with_context({'tracking_disable':True}))astask_form:
                    task_form.name='TestSubtaskincompanyB'
                    task_form.parent_id=self.task_1

                task=task_form.save()

                self.assertEqual(task.project_id,self.task_1.project_id.subtask_project_id,"Thedefaultprojectofasubtaskshouldbethedefaultsubtaskprojectoftheprojectfromthemothertask")
                self.assertEqual(task.company_id,task.project_id.subtask_project_id.company_id,"Thecompanyoftheorphansubtaskshouldbetheonefromitsproject.")
                self.assertEqual(self.task_1.child_ids.ids,[task.id])

        withself.sudo('employee-a'):
            withself.assertRaises(AccessError):
                withForm(task)astask_form:
                    task_form.name="TestingchangingnameinacompanyIcannotread/write"
