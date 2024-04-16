#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

from.test_project_baseimportTestProjectCommon
fromflectra.toolsimportmute_logger
fromflectra.modules.moduleimportget_resource_path


EMAIL_TPL="""Return-Path:<whatever-2a840@postmaster.twitter.com>
X-Original-To:{to}
Delivered-To:{to}
To:{to}
cc:{cc}
Received:bymail1.flectrahq.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
Message-ID:{msg_id}
Date:Tue,29Nov201112:43:21+0530
From:{email_from}
MIME-Version:1.0
Subject:{subject}
Content-Type:text/plain;charset=ISO-8859-1;format=flowed

Hello,

Thisemailshouldcreateanewentryinyourmodule.Pleasecheckthatit
effectivelyworks.

Thanks,

--
RaoulBoitempoils
IntegratoratAgrolait"""


classTestProjectFlow(TestProjectCommon):

    deftest_project_process_project_manager_duplicate(self):
        pigs=self.project_pigs.with_user(self.user_projectmanager)
        dogs=pigs.copy()
        self.assertEqual(len(dogs.tasks),2,'project:duplicatingaprojectmustduplicateitstasks')

    @mute_logger('flectra.addons.mail.mail_thread')
    deftest_task_process_without_stage(self):
        #Do:incomingmailfromanunknownpartneronanaliascreatesanewtask'Frogs'
        task=self.format_and_process(
            EMAIL_TPL,to='project+pigs@mydomain.com,valid.lelitre@agrolait.com',cc='valid.other@gmail.com',
            email_from='%s'%self.user_projectuser.email,
            subject='Frogs',msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='project.task')

        #Test:onetaskcreatedbymailgatewayadministrator
        self.assertEqual(len(task),1,'project:message_process:anewproject.taskshouldhavebeencreated')
        #Test:checkpartnerinmessagefollowers
        self.assertIn(self.partner_2,task.message_partner_ids,"Partnerinmessageccisnotaddedasataskfollowers.")
        #Test:messages
        self.assertEqual(len(task.message_ids),1,
                         'project:message_process:newlycreatedtaskshouldhave1message:email')
        self.assertEqual(task.message_ids[0].subtype_id,self.env.ref('project.mt_task_new'),
                         'project:message_process:firstmessageofnewtaskshouldhaveTaskCreatedsubtype')
        self.assertEqual(task.message_ids[0].author_id,self.user_projectuser.partner_id,
                         'project:message_process:secondmessageshouldbetheonefromAgrolait(partnerfailed)')
        self.assertEqual(task.message_ids[0].subject,'Frogs',
                         'project:message_process:secondmessageshouldbetheonefromAgrolait(subjectfailed)')
        #Test:taskcontent
        self.assertEqual(task.name,'Frogs','project_task:nameshouldbetheemailsubject')
        self.assertEqual(task.project_id.id,self.project_pigs.id,'project_task:incorrectproject')
        self.assertEqual(task.stage_id.sequence,False,"project_task:shouldn'thaveastage,i.e.sequence=False")

    @mute_logger('flectra.addons.mail.mail_thread')
    deftest_task_process_with_stages(self):
        #Do:incomingmailfromanunknownpartneronanaliascreatesanewtask'Cats'
        task=self.format_and_process(
            EMAIL_TPL,to='project+goats@mydomain.com,valid.lelitre@agrolait.com',cc='valid.other@gmail.com',
            email_from='%s'%self.user_projectuser.email,
            subject='Cats',msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='project.task')

        #Test:onetaskcreatedbymailgatewayadministrator
        self.assertEqual(len(task),1,'project:message_process:anewproject.taskshouldhavebeencreated')
        #Test:checkpartnerinmessagefollowers
        self.assertIn(self.partner_2,task.message_partner_ids,"Partnerinmessageccisnotaddedasataskfollowers.")
        #Test:messages
        self.assertEqual(len(task.message_ids),1,
                         'project:message_process:newlycreatedtaskshouldhave1messages:email')
        self.assertEqual(task.message_ids[0].subtype_id,self.env.ref('project.mt_task_new'),
                         'project:message_process:firstmessageofnewtaskshouldhaveTaskCreatedsubtype')
        self.assertEqual(task.message_ids[0].author_id,self.user_projectuser.partner_id,
                         'project:message_process:firstmessageshouldbetheonefromAgrolait(partnerfailed)')
        self.assertEqual(task.message_ids[0].subject,'Cats',
                         'project:message_process:firstmessageshouldbetheonefromAgrolait(subjectfailed)')
        #Test:taskcontent
        self.assertEqual(task.name,'Cats','project_task:nameshouldbetheemailsubject')
        self.assertEqual(task.project_id.id,self.project_goats.id,'project_task:incorrectproject')
        self.assertEqual(task.stage_id.sequence,1,"project_task:shouldhaveastagewithsequence=1")

    @mute_logger('flectra.addons.mail.mail_thread')
    deftest_portal_visibility(self):
        #changeportalvisibilitytotheprojectandaddPortaluserasinvited
        self.project_goats.write({
            'privacy_visibility':'portal',
            'allowed_portal_user_ids':[self.user_portal.id],
        })

        #Do:incomingmailfromaninternaluseronanaliascreatesanewtask'Rabbits'
        task=self.format_and_process(
            EMAIL_TPL,to='project+goats@mydomain.com,valid.lelitre@agrolait.com',cc='valid.other@gmail.com',
            email_from='%s'%self.user_projectmanager.email,
            subject='Rabbits',msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='project.task')

        self.assertIn(self.user_portal,task.allowed_user_ids,'TaskshouldbevisibleforPortalUser')

    deftest_subtask_process(self):
        """
        Checksubtaskmecanismandchangeitfromproject.

        Forthistest,2projectsareused:
            -the'pigs'projectwhichhasapartner_id
            -the'goats'projectwherethepartner_idisremovedatthebeginningofthetestsandthenrestored.

        2parenttasksarealsousedtobeabletoswitchtheparenttaskofasub-task:
            -'parent_task'linkedtothepartner_2
            -'another_parent_task'linkedtothepartner_3
        """

        Task=self.env['project.task'].with_context({'tracking_disable':True})

        parent_task=Task.create({
            'name':'MotherTask',
            'user_id':self.user_projectuser.id,
            'project_id':self.project_pigs.id,
            'partner_id':self.partner_2.id,
            'planned_hours':12,
        })

        another_parent_task=Task.create({
            'name':'AnotherMotherTask',
            'user_id':self.user_projectuser.id,
            'project_id':self.project_pigs.id,
            'partner_id':self.partner_3.id,
            'planned_hours':0,
        })

        #removethepartner_idofthe'goats'project
        goats_partner_id=self.project_goats.partner_id

        self.project_goats.write({
            'partner_id':False
        })

        #thechildtask1islinkedtoaprojectwithoutpartner_id(goatsproject)
        child_task_1=Task.create({
            'name':'TaskChildwithproject',
            'parent_id':parent_task.id,
            'project_id':self.project_goats.id,
            'planned_hours':3,
        })

        #thechildtask2islinkedtoaprojectwithapartner_id(pigsproject)
        child_task_2=Task.create({
            'name':'TaskChildwithoutproject',
            'parent_id':parent_task.id,
            'project_id':self.project_pigs.id,
            'planned_hours':5,
        })

        self.assertEqual(
            child_task_1.partner_id,child_task_1.parent_id.partner_id,
            "Whennoprojectpartner_idhasbeenset,asubtaskshouldhavethesamepartnerasitsparent")

        self.assertEqual(
            child_task_2.partner_id,child_task_2.project_id.partner_id,
            "Whenaprojectpartner_idhasbeenset,asubtaskshouldhavethesamepartnerasitsproject")

        self.assertEqual(
            parent_task.subtask_count,2,
            "Parenttaskshouldhave2children")

        self.assertEqual(
            parent_task.subtask_planned_hours,8,
            "Plannedhoursofsubtaskshouldimpactparenttask")

        #changetheparentofasubtaskwithoutaprojectpartner_id
        child_task_1.write({
            'parent_id':another_parent_task.id
        })

        self.assertEqual(
            child_task_1.partner_id,parent_task.partner_id,
            "Whenchangingtheparenttaskofasubtaskwithnoprojectpartner_id,thepartner_idshouldremainthesame.")

        #changetheparentofasubtaskwithaprojectpartner_id
        child_task_2.write({
            'parent_id':another_parent_task.id
        })

        self.assertEqual(
            child_task_2.partner_id,child_task_2.project_id.partner_id,
            "Whenchangingtheparenttaskofasubtaskwithaproject,thepartner_idshouldremainthesame.")

        #setaprojectwithpartner_idtoasubtaskwithoutprojectpartner_id
        child_task_1.write({
            'project_id':self.project_pigs.id
        })

        self.assertEqual(
            child_task_1.partner_id,self.project_pigs.partner_id,
            "Whentheprojectchanges,thesubtaskshouldhavethesamepartneridasthenewproject.")

        #restorethepartner_idofthe'goats'project
        self.project_goats.write({
            'partner_id':goats_partner_id
        })

        #setaprojectwithpartner_idtoasubtaskwithaprojectpartner_id
        child_task_2.write({
            'project_id':self.project_goats.id
        })

        self.assertEqual(
            child_task_2.partner_id,self.project_goats.partner_id,
            "Whentheprojectchanges,thesubtaskshouldhavethesamepartneridasthenewproject.")

    deftest_rating(self):
        """CheckifratingworkscorrectlyevenwhentaskischangedfromprojectAtoprojectB"""
        Task=self.env['project.task'].with_context({'tracking_disable':True})
        first_task=Task.create({
            'name':'firsttask',
            'user_id':self.user_projectuser.id,
            'project_id':self.project_pigs.id,
            'partner_id':self.partner_2.id,
        })

        self.assertEqual(first_task.rating_count,0,"Taskshouldhavenoratingassociatedwithit")

        rating_good=self.env['rating.rating'].create({
            'res_model_id':self.env['ir.model']._get('project.task').id,
            'res_id':first_task.id,
            'parent_res_model_id':self.env['ir.model']._get('project.project').id,
            'parent_res_id':self.project_pigs.id,
            'rated_partner_id':self.partner_2.id,
            'partner_id':self.partner_2.id,
            'rating':5,
            'consumed':False,
        })

        rating_bad=self.env['rating.rating'].create({
            'res_model_id':self.env['ir.model']._get('project.task').id,
            'res_id':first_task.id,
            'parent_res_model_id':self.env['ir.model']._get('project.project').id,
            'parent_res_id':self.project_pigs.id,
            'rated_partner_id':self.partner_2.id,
            'partner_id':self.partner_2.id,
            'rating':3,
            'consumed':True,
        })

        #WeneedtoinvalidatecachesinceitisnotdoneautomaticallybytheORM
        #OurOne2Manyislinkedtoares_id(int)forwhichtheormdoesn'tcreateaninverse
        first_task.invalidate_cache()

        self.assertEqual(rating_good.rating_text,'satisfied')
        self.assertEqual(rating_bad.rating_text,'not_satisfied')
        self.assertEqual(first_task.rating_count,1,"Taskshouldhaveonlyoneratingassociated,sinceoneisnotconsumed")
        self.assertEqual(rating_good.parent_res_id,self.project_pigs.id)

        self.assertEqual(self.project_goats.rating_percentage_satisfaction,-1)
        self.assertEqual(self.project_pigs.rating_percentage_satisfaction,0) #Thereisaratingbutnota"great"on,justan"okay".

        #Consumingrating_good
        first_task.rating_apply(5,rating_good.access_token)

        #WeneedtoinvalidatecachesinceitisnotdoneautomaticallybytheORM
        #OurOne2Manyislinkedtoares_id(int)forwhichtheormdoesn'tcreateaninverse
        first_task.invalidate_cache()

        self.assertEqual(first_task.rating_count,2,"Taskshouldhavetworatingsassociatedwithit")
        self.assertEqual(rating_good.parent_res_id,self.project_pigs.id)
        self.assertEqual(self.project_goats.rating_percentage_satisfaction,-1)
        self.assertEqual(self.project_pigs.rating_percentage_satisfaction,50)

        #Wechangethetaskfromproject_pigstoproject_goats,ratingsshouldbeassociatedwiththenewproject
        first_task.project_id=self.project_goats.id

        #WeneedtoinvalidatecachesinceitisnotdoneautomaticallybytheORM
        #OurOne2Manyislinkedtoares_id(int)forwhichtheormdoesn'tcreateaninverse
        first_task.invalidate_cache()

        self.assertEqual(rating_good.parent_res_id,self.project_goats.id)
        self.assertEqual(self.project_goats.rating_percentage_satisfaction,50)
        self.assertEqual(self.project_pigs.rating_percentage_satisfaction,-1)
