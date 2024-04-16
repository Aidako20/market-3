#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon
fromflectra.addons.hr.tests.commonimportTestHrCommon
fromflectra.modules.moduleimportget_module_resource


classTestRecruitmentProcess(TestHrCommon):

    deftest_00_recruitment_process(self):
        """Testrecruitmentprocess"""

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

        #CreateanewHRRecruitmentOfficer
        self.res_users_hr_recruitment_officer=self.env['res.users'].create({
            'company_id':self.env.ref('base.main_company').id,
            'name':'HRRecruitmentOfficer',
            'login':"hrro",
            'email':"hrofcr@yourcompany.com",
            'groups_id':[(6,0,[self.env.ref('hr_recruitment.group_hr_recruitment_user').id])]
        })

        #Anapplicantisinterestedinthejobposition.Sohesendsaresumebyemail.
        #InOrdertotestprocessofRecruitmentsogivingHRofficer'srights
        withopen(get_module_resource('hr_recruitment','tests','resume.eml'),'rb')asrequest_file:
            request_message=request_file.read()
        self.env['mail.thread'].with_user(self.res_users_hr_recruitment_officer).message_process(
            'hr.applicant',request_message,custom_values={"job_id":self.job_developer.id})

        #Aftergettingthemail,Icheckthedetailsofthenewapplicant.
        applicant=self.env['hr.applicant'].search([('email_from','ilike','Richard_Anderson@yahoo.com')],limit=1)
        self.assertTrue(applicant,"Applicantisnotcreatedaftergettingthemail")
        resume_ids=self.env['ir.attachment'].search([
            ('name','=','resume.pdf'),
            ('res_model','=',self.env['hr.applicant']._name),
            ('res_id','=',applicant.id)])
        self.assertEqual(applicant.name,'ApplicationforthepostofJr.applicationProgrammer.','Applicantnamedoesnotmatch.')
        self.assertEqual(applicant.stage_id,self.env.ref('hr_recruitment.stage_job1'),
            "Stageshouldbe'Initialqualification'andis'%s'."%(applicant.stage_id.name))
        self.assertTrue(resume_ids,'Resumeisnotattached.')
        #IassigntheJobpositiontotheapplicant
        applicant.write({'job_id':self.job_developer.id})
        #Ischedulemeetingwithapplicantforinterview.
        applicant_meeting=applicant.action_makeMeeting()
        self.assertEqual(applicant_meeting['context']['default_name'],'ApplicationforthepostofJr.applicationProgrammer.',
            'Applicantnamedoesnotmatch.')
