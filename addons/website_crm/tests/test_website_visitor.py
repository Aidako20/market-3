#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.crm.tests.commonimportTestCrmCommon
fromflectra.tests.commonimportusers


classTestWebsiteVisitor(TestCrmCommon):

    defsetUp(self):
        super(TestWebsiteVisitor,self).setUp()
        self.test_partner=self.env['res.partner'].create({
            'name':'TestCustomer',
            'email':'"TestCustomer"<test@test.example.com>',
            'country_id':self.env.ref('base.be').id,
            'mobile':'+32456001122'
        })

    @users('user_sales_manager')
    deftest_compute_email_phone(self):
        visitor_sudo=self.env['website.visitor'].sudo().create({
            'name':'MegaVisitor',
        })
        visitor=visitor_sudo.with_user(self.env.user) #asof13.0salesmencannotcreatevisitors,onlyreadthem
        customer=self.test_partner.with_user(self.env.user)
        self.assertFalse(visitor.email)
        self.assertFalse(visitor.mobile)

        #partnerinformationcopiedonvisitor->behaveslikerelated
        visitor_sudo.write({'partner_id':self.test_partner.id})
        self.assertEqual(visitor.email,customer.email_normalized)
        self.assertEqual(visitor.mobile,customer.mobile)

        #ifreset->behaveslikearelated,alsoresetonvisitor
        visitor_sudo.write({'partner_id':False})
        self.assertFalse(visitor.email)
        self.assertFalse(visitor.mobile)

        #firstleadcreated->updatesemail
        lead_1=self.env['crm.lead'].create({
            'name':'TestLead1',
            'email_from':'RambeauFort<beaufort@test.example.com',
            'visitor_ids':[(4,visitor.id)],
        })
        self.assertEqual(visitor.email,lead_1.email_normalized)
        self.assertFalse(visitor.mobile)

        #secondleadcreated->keepfirstemailbuttakesmobileasnotdefinedbefore
        lead_2=self.env['crm.lead'].create({
            'name':'TestLead1',
            'email_from':'MartinoBrie<brie@test.example.com',
            'country_id':self.env.ref('base.be').id,
            'mobile':'+32456001122',
            'visitor_ids':[(4,visitor.id)],
        })
        self.assertEqual(visitor.email,lead_1.email_normalized)
        self.assertEqual(visitor.mobile,lead_2.mobile)

        #partnerwinonleads
        visitor_sudo.write({'partner_id':self.test_partner.id})
        self.assertEqual(visitor.email,customer.email_normalized)
        self.assertEqual(visitor.mobile,customer.mobile)

        #partnerupdated->fallbackonleads
        customer.write({'mobile':False})
        self.assertEqual(visitor.email,customer.email_normalized)
        self.assertEqual(visitor.mobile,lead_2.mobile)
