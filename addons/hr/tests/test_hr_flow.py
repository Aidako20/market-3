#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.hr.tests.commonimportTestHrCommon


classTestHrFlow(TestHrCommon):

    defsetUp(self):
        super(TestHrFlow,self).setUp()
        self.dep_rd=self.env['hr.department'].create({
            'name':'Research&Development',
        })
        self.job_developer=self.env['hr.job'].create({
            'name':'ExperiencedDeveloper',
            'department_id':self.dep_rd.id,
            'no_of_recruitment':5,
        })
        self.employee_niv=self.env['hr.employee'].create({
            'name':'SharleneRhodes',
        })
        self.job_developer=self.job_developer.with_user(self.res_users_hr_officer.id)
        self.employee_niv=self.employee_niv.with_user(self.res_users_hr_officer.id)

    deftest_open2recruit2close_job(self):

        """Openingthejobpositionfor"Developer"andcheckingthejobstatusandrecruitmentcount."""
        self.job_developer.set_open()
        self.assertEqual(self.job_developer.state,'open',"Jobpositionof'JobDeveloper'isin'open'state.")
        self.assertEqual(self.job_developer.no_of_recruitment,0,
             "Wrongnumberofrecruitmentforthejob'JobDeveloper'(%sfoundinsteadof0)."
             %self.job_developer.no_of_recruitment)

        """Recruitingemployee"NIV"forthejobposition"Developer"andcheckingthejobstatusandrecruitmentcount."""
        self.job_developer.set_recruit()
        self.assertEqual(self.job_developer.state,'recruit',"Jobpositionof'JobDeveloper'isin'recruit'state.")
        self.assertEqual(self.job_developer.no_of_recruitment,1,
             "Wrongnumberofrecruitmentforthejob'JobDeveloper'(%sfoundinsteadof1.0)."
             %self.job_developer.no_of_recruitment)

        self.employee_niv.write({'job_id':self.job_developer.id})

        """Closingtherecruitmentforthejobposition"Developer"bymarkingitasopen."""
        self.job_developer.set_open()
        self.assertEqual(self.job_developer.state,'open',"Jobpositionof'JobDeveloper'isin'open'state.")
        self.assertEqual(self.job_developer.no_of_recruitment,0,
             "Wrongnumberofrecruitmentforthejob'JobDeveloper'(%sfoundinsteadof0)."
             %self.job_developer.no_of_recruitment)
