#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectra.addons.crm.testsimportcommonascrm_common
fromflectra.tests.commonimporttagged,users


@tagged('lead_manage')
classTestLeadConvertToTicket(crm_common.TestCrmCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestLeadConvertToTicket,cls).setUpClass()
        cls.lead_1.write({
            'user_id':cls.user_sales_salesman.id,
        })

    @users('user_sales_salesman')
    deftest_lead_convert_to_quotation_create(self):
        """Testpartnercreationwhileconverting"""
        #Performinitialtests,donotrepeatthemateachtest
        lead=self.lead_1.with_user(self.env.user)
        self.assertEqual(lead.partner_id,self.env['res.partner'])
        new_partner=self.env['res.partner'].search([('email_normalized','=','amy.wong@test.example.com')])
        self.assertEqual(new_partner,self.env['res.partner'])

        #invokewizardandapplyit
        convert=self.env['crm.quotation.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id
        }).create({})

        self.assertEqual(convert.action,'create')
        self.assertEqual(convert.partner_id,self.env['res.partner'])

        action=convert.action_apply()

        #testleadupdate
        new_partner=self.env['res.partner'].search([('email_normalized','=','amy.wong@test.example.com')])
        self.assertEqual(lead.partner_id,new_partner)

        #testwizardaction(doesnotcreateanything,justreturnsaction)
        self.assertEqual(action['res_model'],'sale.order')
        self.assertEqual(action['context']['default_partner_id'],new_partner.id)

    @users('user_sales_salesman')
    deftest_lead_convert_to_quotation_exist(self):
        """Testtakingonlyexistingcustomerwhileconverting"""
        lead=self.lead_1.with_user(self.env.user)

        #invokewizardandapplyit
        convert=self.env['crm.quotation.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id
        }).create({'action':'exist'})

        self.assertEqual(convert.action,'exist')
        self.assertEqual(convert.partner_id,self.env['res.partner'])

        action=convert.action_apply()

        #testleadupdate
        new_partner=self.env['res.partner'].search([('email_normalized','=','amy.wong@test.example.com')])
        self.assertEqual(new_partner,self.env['res.partner'])

        convert.write({'partner_id':self.contact_2.id})
        action=convert.action_apply()

        #testleadupdate
        new_partner=self.env['res.partner'].search([('email_normalized','=','amy.wong@test.example.com')])
        self.assertEqual(new_partner,self.env['res.partner'])
        self.assertEqual(lead.partner_id,self.contact_2)
        #TDETODO:havearealsyncassertforlead/contact
        self.assertEqual(lead.email_from,self.contact_2.email)
        self.assertEqual(lead.mobile,self.contact_2.mobile)
        self.assertEqual(action['context']['default_partner_id'],self.contact_2.id)

    @users('user_sales_salesman')
    deftest_lead_convert_to_quotation_false_match_create(self):
        lead=self.lead_1.with_user(self.env.user)

        #invokewizardandapplyit
        convert=self.env['crm.quotation.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id,
        }).create({'action':'create'})

        convert.write({'partner_id':self.contact_2.id})

        self.assertEqual(convert.action,'create')

        #ignorematchingpartnerandcreateanewone
        convert.action_apply()

        self.assertTrue(bool(lead.partner_id.id))
        self.assertNotEqual(lead.partner_id,self.contact_2)

    @users('user_sales_salesman')
    deftest_lead_convert_to_quotation_nothing(self):
        """Testdoingnothingaboutcustomerwhileconverting"""
        lead=self.lead_1.with_user(self.env.user)

        #invokewizardandapplyit
        convert=self.env['crm.quotation.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id,
            'default_action':'nothing',
        }).create({})

        self.assertEqual(convert.action,'nothing')
        self.assertEqual(convert.partner_id,self.env['res.partner'])

        action=convert.action_apply()

        #testleadupdate
        new_partner=self.env['res.partner'].search([('email_normalized','=','amy.wong@test.example.com')])
        self.assertEqual(new_partner,self.env['res.partner'])
        self.assertEqual(lead.partner_id,self.env['res.partner'])
        self.assertEqual(action['context']['default_partner_id'],False)
