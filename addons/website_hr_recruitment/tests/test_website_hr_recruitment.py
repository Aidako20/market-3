#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.apiimportEnvironment
importflectra.tests

@flectra.tests.tagged('post_install','-at_install')
classTestWebsiteHrRecruitmentForm(flectra.tests.HttpCase):
    deftest_tour(self):
        job_guru=self.env['hr.job'].create({
            'name':'Guru',
            'is_published':True,
        })
        job_intern=self.env['hr.job'].create({
            'name':'Internship',
            'is_published':True,
        })
        self.start_tour('/','website_hr_recruitment_tour_edit_form',login='admin')
        self.start_tour('/','website_hr_recruitment_tour')

        #checkresult
        guru_applicant=self.env['hr.applicant'].search([('description','=','###[GURU]HRRECRUITMENTTESTDATA###'),
                                                        ('job_id','=',job_guru.id),])
        self.assertEqual(len(guru_applicant),1)
        self.assertEqual(guru_applicant.partner_name,'JohnSmith')
        self.assertEqual(guru_applicant.email_from,'john@smith.com')
        self.assertEqual(guru_applicant.partner_phone,'118.218')

        internship_applicant=self.env['hr.applicant'].search([('description','=','###HR[INTERN]RECRUITMENTTESTDATA###'),
                                                                ('job_id','=',job_intern.id),])
        self.assertEqual(len(internship_applicant),1)
        self.assertEqual(internship_applicant.partner_name,'JackDoe')
        self.assertEqual(internship_applicant.email_from,'jack@doe.com')
        self.assertEqual(internship_applicant.partner_phone,'118.712')
