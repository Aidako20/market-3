#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestWebsiteCrm(flectra.tests.HttpCase):

    deftest_tour(self):
        self.start_tour("/",'website_crm_tour')

        #checkresult
        record=self.env['crm.lead'].search([('description','=','###TOURDATA###')])
        self.assertEqual(len(record),1)
        self.assertEqual(record.contact_name,'JohnSmith')
        self.assertEqual(record.email_from,'john@smith.com')
        self.assertEqual(record.partner_name,'FlectraS.A.')
