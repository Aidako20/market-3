#-*-coding:utf-8-*-

fromflectra.tests.commonimportSavepointCase
fromflectra.exceptionsimportUserError

classTestProjectCommon(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestProjectCommon,cls).setUpClass()

        user_group_employee=cls.env.ref('base.group_user')
        user_group_project_user=cls.env.ref('project.group_project_user')
        user_group_project_manager=cls.env.ref('project.group_project_manager')

        cls.partner_1=cls.env['res.partner'].create({
            'name':'ValidLelitre',
            'email':'valid.lelitre@agrolait.com'})
        cls.partner_2=cls.env['res.partner'].create({
            'name':'ValidPoilvache',
            'email':'valid.other@gmail.com'})
        cls.partner_3=cls.env['res.partner'].create({
            'name':'ValidPoilboeuf',
            'email':'valid.poilboeuf@gmail.com'})

        #Testuserstousethroughthevarioustests
        Users=cls.env['res.users'].with_context({'no_reset_password':True})
        cls.user_public=Users.create({
            'name':'BertTartignole',
            'login':'bert',
            'email':'b.t@example.com',
            'signature':'SignBert',
            'notification_type':'email',
            'groups_id':[(6,0,[cls.env.ref('base.group_public').id])]})
        cls.user_portal=Users.create({
            'name':'ChellGladys',
            'login':'chell',
            'email':'chell@gladys.portal',
            'signature':'SignChell',
            'notification_type':'email',
            'groups_id':[(6,0,[cls.env.ref('base.group_portal').id])]})
        cls.user_projectuser=Users.create({
            'name':'ArmandeProjectUser',
            'login':'Armande',
            'email':'armande.projectuser@example.com',
            'groups_id':[(6,0,[user_group_employee.id,user_group_project_user.id])]
        })
        cls.user_projectmanager=Users.create({
            'name':'BastienProjectManager',
            'login':'bastien',
            'email':'bastien.projectmanager@example.com',
            'groups_id':[(6,0,[user_group_employee.id,user_group_project_manager.id])]})

        #Test'Pigs'project
        cls.project_pigs=cls.env['project.project'].with_context({'mail_create_nolog':True}).create({
            'name':'Pigs',
            'privacy_visibility':'employees',
            'alias_name':'project+pigs',
            'partner_id':cls.partner_1.id})
        #Already-existingtasksinPigs
        cls.task_1=cls.env['project.task'].with_context({'mail_create_nolog':True}).create({
            'name':'PigsUserTask',
            'user_id':cls.user_projectuser.id,
            'project_id':cls.project_pigs.id})
        cls.task_2=cls.env['project.task'].with_context({'mail_create_nolog':True}).create({
            'name':'PigsManagerTask',
            'user_id':cls.user_projectmanager.id,
            'project_id':cls.project_pigs.id})

        #Test'Goats'project,sameas'Pigs',butwith2stages
        cls.project_goats=cls.env['project.project'].with_context({'mail_create_nolog':True}).create({
            'name':'Goats',
            'privacy_visibility':'followers',
            'alias_name':'project+goats',
            'partner_id':cls.partner_1.id,
            'type_ids':[
                (0,0,{
                    'name':'New',
                    'sequence':1,
                }),
                (0,0,{
                    'name':'Won',
                    'sequence':10,
                })]
            })

    defformat_and_process(self,template,to='groups@example.com,other@gmail.com',subject='Frogs',
                           extra='',email_from='SylvieLelitre<test.sylvie.lelitre@agrolait.com>',
                           cc='',msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
                           model=None,target_model='project.task',target_field='name'):
        self.assertFalse(self.env[target_model].search([(target_field,'=',subject)]))
        mail=template.format(to=to,subject=subject,cc=cc,extra=extra,email_from=email_from,msg_id=msg_id)
        self.env['mail.thread'].with_context(mail_channel_noautofollow=True).message_process(model,mail)
        returnself.env[target_model].search([(target_field,'=',subject)])

    deftest_delete_project_with_tasks(self):
        """Usershouldneverbeabletodeleteaprojectwithtasks"""

        withself.assertRaises(UserError):
            self.project_pigs.unlink()

        #clickonthearchivebutton
        self.project_pigs.write({'active':False})

        withself.assertRaises(UserError):
            self.project_pigs.unlink()

    deftest_auto_assign_stages_when_importing_tasks(self):
        self.assertFalse(self.project_pigs.type_ids)
        self.assertEqual(len(self.project_goats.type_ids),2)
        first_stage=self.project_goats.type_ids[0]
        self.env['project.task']._load_records_create({
            'name':'FirstTask',
            'user_id':self.user_projectuser.id,
            'project_id':self.project_pigs.id,
            'stage_id':first_stage.id,
        })
        self.assertEqual(self.project_pigs.type_ids,first_stage)
        self.env['project.task']._load_records_create([
            {'name':'task',
                'user_id':self.user_projectuser.id,
                'project_id':self.project_pigs.id,
                'stage_id':stage.id,
            }forstageinself.project_goats.type_ids
        ])
        self.assertEqual(self.project_pigs.type_ids,self.project_goats.type_ids)
