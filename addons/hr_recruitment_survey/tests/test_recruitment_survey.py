#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon


classTestRecruitmentSurvey(common.SingleTransactionCase):

    @classmethod
    defsetUpClass(cls):
        super(TestRecruitmentSurvey,cls).setUpClass()

        #Createsomesampledatatoavoiddemodata
        cls.department_admins=cls.env['hr.department'].create({'name':'Admins'})
        cls.survey_sysadmin=cls.env['survey.survey'].create({'title':'QuestionsforSysadminjoboffer'})

        cls.job=cls.env['hr.job'].create({
            'name':'Technicalworker',
            'survey_id':cls.survey_sysadmin.id,
        })
        cls.job_sysadmin=cls.env['hr.applicant'].create({
            'name':'Technicalworker',
            'department_id':cls.department_admins.id,
            'description':'AniceSysAdminjoboffer!',
            'job_id':cls.job.id,
        })

    deftest_start_survey(self):
        #WeensurethatresponseisFalsebecausewedon'tknowtestorder
        self.job_sysadmin.response_id=False
        action_start=self.job_sysadmin.action_start_survey()
        self.assertEqual(action_start['type'],'ir.actions.act_url')
        self.assertNotEqual(self.job_sysadmin.response_id.id,False)
        self.assertIn(self.job_sysadmin.response_id.access_token,action_start['url'])
        action_start_with_response=self.job_sysadmin.action_start_survey()
        self.assertEqual(action_start_with_response,action_start)

    deftest_print_survey(self):
        #WeensurethatresponseisFalsebecausewedon'tknowtestorder
        self.job_sysadmin.response_id=False
        action_print=self.job_sysadmin.action_print_survey()
        self.assertEqual(action_print['type'],'ir.actions.act_url')
        self.job_sysadmin.response_id=self.env['survey.user_input'].create({'survey_id':self.survey_sysadmin.id})
        action_print_with_response=self.job_sysadmin.action_print_survey()
        self.assertIn(self.job_sysadmin.response_id.access_token,action_print_with_response['url'])
