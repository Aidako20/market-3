##-*-coding:utf-8-*-
##PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch
importsys

fromflectra.addons.base.tests.commonimportTransactionCaseWithUserDemo
fromflectra.testsimportcommon,tagged
fromflectra.exceptionsimportAccessError


@tagged('post_install','-at_install')
classBaseAutomationTest(TransactionCaseWithUserDemo):

    defsetUp(self):
        super(BaseAutomationTest,self).setUp()
        self.user_root=self.env.ref('base.user_root')
        self.user_admin=self.env.ref('base.user_admin')

        self.test_mail_template_automation=self.env['mail.template'].create({
            'name':'TemplateAutomation',
            'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
            'body_html':"""&lt;div&gt;Emailautomation&lt;/div&gt;""",
        })

        self.res_partner_1=self.env['res.partner'].create({'name':'MyPartner'})
        self.env['base.automation'].create([
            {
                'name':'BaseAutomation:testruleoncreate',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'state':'code',
                'code':"records.write({'user_id':%s})"%(self.user_demo.id),
                'trigger':'on_create',
                'active':True,
                'filter_domain':"[('state','=','draft')]",
            },{
                'name':'BaseAutomation:testruleonwrite',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'state':'code',
                'code':"records.write({'user_id':%s})"%(self.user_demo.id),
                'trigger':'on_write',
                'active':True,
                'filter_domain':"[('state','=','done')]",
                'filter_pre_domain':"[('state','=','open')]",
            },{
                'name':'BaseAutomation:testruleonrecompute',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'state':'code',
                'code':"records.write({'user_id':%s})"%(self.user_demo.id),
                'trigger':'on_write',
                'active':True,
                'filter_domain':"[('employee','=',True)]",
            },{
                'name':'BaseAutomation:testrecursiverule',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'state':'code',
                'code':"""
record=model.browse(env.context['active_id'])
if'partner_id'inenv.context['old_values'][record.id]:
    record.write({'state':'draft'})""",
                'trigger':'on_write',
                'active':True,
            },{
                'name':'BaseAutomation:testruleonsecondarymodel',
                'model_id':self.env.ref('test_base_automation.model_base_automation_line_test').id,
                'state':'code',
                'code':"records.write({'user_id':%s})"%(self.user_demo.id),
                'trigger':'on_create',
                'active':True,
            },{
                'name':'BaseAutomation:testruleonwritecheckcontext',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'state':'code',
                'code':"""
record=model.browse(env.context['active_id'])
if'user_id'inenv.context['old_values'][record.id]:
    record.write({'is_assigned_to_admin':(record.user_id.id==1)})""",
                'trigger':'on_write',
                'active':True,
            },{
                'name':'BaseAutomation:testrulewithtrigger',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'trigger_field_ids':[(4,self.env.ref('test_base_automation.field_base_automation_lead_test__state').id)],
                'state':'code',
                'code':"""
record=model.browse(env.context['active_id'])
record['name']=record.name+'X'""",
                'trigger':'on_write',
                'active':True,
            },{
                'name':'BaseAutomation:testsendanemail',
                'model_id':self.env.ref('test_base_automation.model_base_automation_lead_test').id,
                'template_id':self.test_mail_template_automation.id,
                'trigger_field_ids':[(4,self.env.ref('test_base_automation.field_base_automation_lead_test__deadline').id)],
                'state':'email',
                'code':"""
record=model.browse(env.context['active_id'])
record['name']=record.name+'X'""",
                'trigger':'on_write',
                'active':True,
                'filter_domain':"[('deadline','!=',False)]",
                'filter_pre_domain':"[('deadline','=',False)]",
            }
        ])

    deftearDown(self):
        super().tearDown()
        self.env['base.automation']._unregister_hook()

    defcreate_lead(self,**kwargs):
        vals={
            'name':"LeadTest",
            'user_id':self.user_root.id,
        }
        vals.update(kwargs)
        returnself.env['base.automation.lead.test'].create(vals)

    deftest_00_check_to_state_open_pre(self):
        """
        Checkthatanewrecord(withstate=open)doesn'tchangeitsresponsible
        whenthereisapreconditionfilterwhichcheckthatthestateisopen.
        """
        lead=self.create_lead(state='open')
        self.assertEqual(lead.state,'open')
        self.assertEqual(lead.user_id,self.user_root,"ResponsibleshouldnotchangeoncreationofLeadwithstate'open'.")

    deftest_01_check_to_state_draft_post(self):
        """
        Checkthatanewrecordchangesitsresponsiblewhenthereisapostcondition
        filterwhichcheckthatthestateisdraft.
        """
        lead=self.create_lead()
        self.assertEqual(lead.state,'draft',"Leadstateshouldbe'draft'")
        self.assertEqual(lead.user_id,self.user_demo,"ResponsibleshouldbechangeoncreationofLeadwithstate'draft'.")

    deftest_02_check_from_draft_to_done_with_steps(self):
        """
        Anewrecordiscreatedandgoesfromstates'open'to'done'viathe
        otherstates(open,pendingandcancel).Wehavearulewith:
         -precondition:therecordisin"open"
         -postcondition:thattherecordis"done".
        Ifthestategoesfrom'open'to'done'theresponsibleischanged.
        Ifthosetwoconditionsaren'tverified,theresponsibleremainsthesame.
        """
        lead=self.create_lead(state='open')
        self.assertEqual(lead.state,'open',"Leadstateshouldbe'open'")
        self.assertEqual(lead.user_id,self.user_root,"ResponsibleshouldnotchangeoncreationofLeadwithstate'open'.")
        #changestatetopendingandcheckthatresponsiblehasnotchanged
        lead.write({'state':'pending'})
        self.assertEqual(lead.state,'pending',"Leadstateshouldbe'pending'")
        self.assertEqual(lead.user_id,self.user_root,"ResponsibleshouldnotchangeoncreationofLeadwithstatefrom'draft'to'open'.")
        #changestatetodoneandcheckthatresponsiblehasnotchanged
        lead.write({'state':'done'})
        self.assertEqual(lead.state,'done',"Leadstateshouldbe'done'")
        self.assertEqual(lead.user_id,self.user_root,"ResponsibleshouldnotchangoncreationofLeadwithstatefrom'pending'to'done'.")

    deftest_03_check_from_draft_to_done_without_steps(self):
        """
        Anewrecordiscreatedandgoesfromstates'open'to'done'viathe
        otherstates(open,pendingandcancel).Wehavearulewith:
         -precondition:therecordisin"open"
         -postcondition:thattherecordis"done".
        Ifthestategoesfrom'open'to'done'theresponsibleischanged.
        Ifthosetwoconditionsaren'tverified,theresponsibleremainsthesame.
        """
        lead=self.create_lead(state='open')
        self.assertEqual(lead.state,'open',"Leadstateshouldbe'open'")
        self.assertEqual(lead.user_id,self.user_root,"ResponsibleshouldnotchangeoncreationofLeadwithstate'open'.")
        #changestatetodoneandcheckthatresponsiblehaschanged
        lead.write({'state':'done'})
        self.assertEqual(lead.state,'done',"Leadstateshouldbe'done'")
        self.assertEqual(lead.user_id,self.user_demo,"ResponsibleshouldbechangeonwriteofLeadwithstatefrom'open'to'done'.")

    deftest_10_recomputed_field(self):
        """
        Checkthataruleisexecutedwheneverafieldisrecomputedaftera
        changeonanothermodel.
        """
        partner=self.res_partner_1
        partner.write({'employee':False})
        lead=self.create_lead(state='open',partner_id=partner.id)
        self.assertFalse(lead.employee,"CustomerfieldshouldupdatedtoFalse")
        self.assertEqual(lead.user_id,self.user_root,"ResponsibleshouldnotchangeoncreationofLeadwithstatefrom'draft'to'open'.")
        #changepartner,recomputeonleadshouldtriggertherule
        partner.write({'employee':True})
        lead.flush()
        self.assertTrue(lead.employee,"CustomerfieldshouldupdatedtoTrue")
        self.assertEqual(lead.user_id,self.user_demo,"ResponsibleshouldbechangeonwriteofLeadwhenCustomerbecomesTrue.")

    deftest_11_recomputed_field(self):
        """
        Checkthataruleisexecutedwheneverafieldisrecomputedandthe
        contextcontainsthetargetfield
        """
        partner=self.res_partner_1
        lead=self.create_lead(state='draft',partner_id=partner.id)
        self.assertFalse(lead.deadline,'Thereshouldnotbeadeadlinedefined')
        #changepriorityanduser;thistriggersdeadlinerecomputation,and
        #theserveractionshouldsetthebooleanfieldtoTrue
        lead.write({'priority':True,'user_id':self.user_root.id})
        self.assertTrue(lead.deadline,'Deadlineshouldbedefined')
        self.assertTrue(lead.is_assigned_to_admin,'Leadshouldbeassignedtoadmin')

    deftest_11b_recomputed_field(self):
        mail_automation=self.env['base.automation'].search([('name','=','BaseAutomation:testsendanemail')])
        send_mail_count=0

        def_patched_get_actions(*args,**kwargs):
            obj=args[0]
            if'__action_done'notinobj._context:
                obj=obj.with_context(__action_done={})
            returnmail_automation.with_env(obj.env)

        def_patched_send_mail(*args,**kwargs):
            nonlocalsend_mail_count
            send_mail_count+=1

        patchers=[
            patch('flectra.addons.base_automation.models.base_automation.BaseAutomation._get_actions',_patched_get_actions),
            patch('flectra.addons.mail.models.mail_template.MailTemplate.send_mail',_patched_send_mail),
        ]

        patchers[0].start()

        lead=self.create_lead()
        self.assertFalse(lead.priority)
        self.assertFalse(lead.deadline)

        patchers[1].start()

        lead.write({'priority':True})

        self.assertTrue(lead.priority)
        self.assertTrue(lead.deadline)

        forpatcherinpatchers:
            patcher.stop()

        self.assertEqual(send_mail_count,1)

    deftest_12_recursive(self):
        """Checkthataruleisexecutedrecursivelybyasecondarychange."""
        lead=self.create_lead(state='open')
        self.assertEqual(lead.state,'open')
        self.assertEqual(lead.user_id,self.user_root)
        #changepartner;thisshouldtriggertherulethatmodifiesthestate
        partner=self.res_partner_1
        lead.write({'partner_id':partner.id})
        self.assertEqual(lead.state,'draft')

    deftest_20_direct_line(self):
        """
        Checkthataruleisexecutedaftercreatingalinerecord.
        """
        line=self.env['base.automation.line.test'].create({'name':"Line"})
        self.assertEqual(line.user_id,self.user_demo)

    deftest_20_indirect_line(self):
        """
        Checkthatcreatingaleadwithalineexecutesrulesonbothrecords.
        """
        lead=self.create_lead(line_ids=[(0,0,{'name':"Line"})])
        self.assertEqual(lead.state,'draft',"Leadstateshouldbe'draft'")
        self.assertEqual(lead.user_id,self.user_demo,"ResponsibleshouldchangeoncreationofLeadtestline.")
        self.assertEqual(len(lead.line_ids),1,"Newtestlineisnotcreated")
        self.assertEqual(lead.line_ids.user_id,self.user_demo,"ResponsibleshouldbechangeoncreationofLeadtestline.")

    deftest_21_trigger_fields(self):
        """
        Checkthattherulewithtriggerisexecutedonlyonceperpertinentupdate.
        """
        lead=self.create_lead(name="X")
        lead.priority=True
        partner1=self.res_partner_1
        lead.partner_id=partner1.id
        self.assertEqual(lead.name,'X',"Noupdateuntilnow.")

        lead.state='open'
        self.assertEqual(lead.name,'XX',"Oneupdateshouldhavehappened.")
        lead.state='done'
        self.assertEqual(lead.name,'XXX',"Oneupdateshouldhavehappened.")
        lead.state='done'
        self.assertEqual(lead.name,'XXX',"Noupdateshouldhavehappened.")
        lead.state='cancel'
        self.assertEqual(lead.name,'XXXX',"Oneupdateshouldhavehappened.")

        #changetheruletotriggeronpartner_id
        rule=self.env['base.automation'].search([('name','=','BaseAutomation:testrulewithtrigger')])
        rule.write({'trigger_field_ids': [(6,0,[self.env.ref('test_base_automation.field_base_automation_lead_test__partner_id').id])]})

        partner2=self.env['res.partner'].create({'name':'Anewpartner'})
        lead.name='X'
        lead.state='open'
        self.assertEqual(lead.name,'X',"Noupdateshouldhavehappened.")
        lead.partner_id=partner2
        self.assertEqual(lead.name,'XX',"Oneupdateshouldhavehappened.")
        lead.partner_id=partner2
        self.assertEqual(lead.name,'XX',"Noupdateshouldhavehappened.")
        lead.partner_id=partner1
        self.assertEqual(lead.name,'XXX',"Oneupdateshouldhavehappened.")

    deftest_30_modelwithoutaccess(self):
        """
        EnsureadomainonaM2Owithoutuseraccessdoesn'tfail.
        Wecreateabaseautomationwithafilteronamodeltheuserhaven'taccessto
        -createagroup
        -restrictacltothisgroupandsetonlyadmininit
        -createbase.automationwithafilter
        -createarecordintherestrictedmodelinadmin
        -createarecordinthenonrestrictedmodelindemo
        """
        Model=self.env['base.automation.link.test']
        Comodel=self.env['base.automation.linked.test']

        access=self.env.ref("test_base_automation.access_base_automation_linked_test")
        access.group_id=self.env['res.groups'].create({
            'name':"Accesstobase.automation.linked.test",
            "users":[(6,0,[self.user_admin.id,])]
        })

        #sanitycheck:userdemohasnoaccesstothecomodelof'linked_id'
        withself.assertRaises(AccessError):
            Comodel.with_user(self.user_demo).check_access_rights('read')

        #checkbaseautomationwithfilterthatperformsComodel.search()
        self.env['base.automation'].create({
            'name':'testnoaccess',
            'model_id':self.env['ir.model']._get_id("base.automation.link.test"),
            'trigger':'on_create_or_write',
            'filter_pre_domain':"[('linked_id.another_field','=','something')]",
            'state':'code',
            'active':True,
            'code':"action=[rec.nameforrecinrecords]"
        })
        Comodel.create([
            {'name':'afirstrecord','another_field':'something'},
            {'name':'anotherrecord','another_field':'somethingdifferent'},
        ])
        rec1=Model.create({'name':'arecord'})
        rec1.write({'name':'afirstrecord'})
        rec2=Model.with_user(self.user_demo).create({'name':'anotherrecord'})
        rec2.write({'name':'anothervalue'})

        #checkbaseautomationwithfilterthatperformsComodel.name_search()
        self.env['base.automation'].create({
            'name':'testnonameaccess',
            'model_id':self.env['ir.model']._get_id("base.automation.link.test"),
            'trigger':'on_create_or_write',
            'filter_pre_domain':"[('linked_id','=','whatever')]",
            'state':'code',
            'active':True,
            'code':"action=[rec.nameforrecinrecords]"
        })
        rec3=Model.create({'name':'arandomrecord'})
        rec3.write({'name':'afirstrecord'})
        rec4=Model.with_user(self.user_demo).create({'name':'againanotherrecord'})
        rec4.write({'name':'anothervalue'})


@common.tagged('post_install','-at_install')
classTestCompute(common.TransactionCase):
    deftest_inversion(self):
        """IfastoredfieldBdependsonA,anupdatetothetriggerforA
        shouldtriggertherecomputatonofA,thenB.

        Howeverifasearch()isperformedduringthecomputationofA
        ???and_orderisaffected???aflushwillbetriggered,forcingthe
        computationofB,basedonthepreviousA.

        Thishappensifarulehashasanon-emptyfilter_pre_domain,evenif
        it'sanemptylist(``'[]'``asopposedto``False``).
        """
        company1=self.env['res.partner'].create({
            'name':"Gorofy",
            'is_company':True,
        })
        company2=self.env['res.partner'].create({
            'name':"Awiclo",
            'is_company':True
        })
        r=self.env['res.partner'].create({
            'name':'Bob',
            'is_company':False,
            'parent_id':company1.id
        })
        self.assertEqual(r.display_name,'Gorofy,Bob')
        r.parent_id=company2
        self.assertEqual(r.display_name,'Awiclo,Bob')

        self.env['base.automation'].create({
            'name':"testrule",
            'filter_pre_domain':False,
            'trigger':'on_create_or_write',
            'state':'code',#no-opaction
            'model_id':self.env.ref('base.model_res_partner').id,
        })
        r.parent_id=company1
        self.assertEqual(r.display_name,'Gorofy,Bob')

        self.env['base.automation'].create({
            'name':"testrule",
            'filter_pre_domain':'[]',
            'trigger':'on_create_or_write',
            'state':'code',#no-opaction
            'model_id':self.env.ref('base.model_res_partner').id,
        })
        r.parent_id=company2
        self.assertEqual(r.display_name,'Awiclo,Bob')

    deftest_recursion(self):
        project=self.env['test_base_automation.project'].create({})

        #thisactionisexecutedeverytimeataskisassignedtoproject
        self.env['base.automation'].create({
            'name':'dummy',
            'model_id':self.env['ir.model']._get_id('test_base_automation.task'),
            'state':'code',
            'trigger':'on_create_or_write',
            'filter_domain':repr([('project_id','=',project.id)]),
        })

        #createonetaskinprojectwith10subtasks;allthesubtasksare
        #automaticallyassignedtoproject,too
        task=self.env['test_base_automation.task'].create({'project_id':project.id})
        subtasks=task.create([{'parent_id':task.id}for_inrange(10)])
        subtasks.flush()

        #Thistestcheckswhathappenswhenastoredrecursivecomputedfield
        #ismarkedtocomputeonmanyrecords,andautomatedactionsare
        #triggereddependingonthatfield. Inthiscase,wetriggerthe
        #recomputationof'project_id'on'subtasks'bydeletingtheirparent
        #task.
        #
        #Anissueoccurswhenthedomainofautomatedactionsisevaluatedby
        #methodsearch(),becausethelatterflushesthefieldstosearchon,
        #whicharealsotheonesbeingrecomputed. Combinedwiththefact
        #thatrecursivefieldsarenotcomputedinbatch,thisleadstoahuge
        #amountofrecursivecallsbetweentheautomatedactionandflush().
        #
        #Theexecutionoftask.unlink()lookslikethis:
        #-mark'project_id'tocomputeonsubtasks
        #-deletetask
        #-flush()
        #  -recompute'project_id'onsubtask1
        #    -callcomputeonsubtask1
        #    -inaction,search([('id','in',subtask1.ids),('project_id','=',pid)])
        #      -flush(['id','project_id'])
        #        -recompute'project_id'onsubtask2
        #          -callcomputeonsubtask2
        #          -inactionsearch([('id','in',subtask2.ids),('project_id','=',pid)])
        #            -flush(['id','project_id'])
        #              -recompute'project_id'onsubtask3
        #                -callcomputeonsubtask3
        #                -inaction,search([('id','in',subtask3.ids),('project_id','=',pid)])
        #                  -flush(['id','project_id'])
        #                    -recompute'project_id'onsubtask4
        #                      ...
        limit=sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(100)
            task.unlink()
        finally:
            sys.setrecursionlimit(limit)
