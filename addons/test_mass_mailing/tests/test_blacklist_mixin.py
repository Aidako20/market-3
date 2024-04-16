#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mass_mailing.models.mailing_modelsimportMailingBLacklist
fromflectra.addons.test_mass_mailing.testsimportcommon
fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportusers


classTestBLMixin(common.TestMassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestBLMixin,cls).setUpClass()

        cls.env['mail.blacklist'].create([{
            'email':'Arya.Stark@example.com',
            'active':True,
        },{
            'email':'Sansa.Stark@example.com',
            'active':False,
        }])

    @users('employee')
    deftest_bl_mixin_primary_field_consistency(self):
        MailingBLacklist._primary_email='not_a_field'
        withself.assertRaises(UserError):
            self.env['mailing.test.blacklist'].search([('is_blacklisted','=',False)])

        MailingBLacklist._primary_email=['not_a_str']
        withself.assertRaises(UserError):
            self.env['mailing.test.blacklist'].search([('is_blacklisted','=',False)])

        MailingBLacklist._primary_email='email_from'
        self.env['mailing.test.blacklist'].search([('is_blacklisted','=',False)])

    @users('employee')
    deftest_bl_mixin_is_blacklisted(self):
        """Testis_blacklistedfieldcomputation"""
        record=self.env['mailing.test.blacklist'].create({'email_from':'arya.stark@example.com'})
        self.assertTrue(record.is_blacklisted)

        record=self.env['mailing.test.blacklist'].create({'email_from':'not.arya.stark@example.com'})
        self.assertFalse(record.is_blacklisted)

    @users('employee')
    deftest_bl_mixin_search_blacklisted(self):
        """Testis_blacklistedfieldsearchimplementation"""
        record1=self.env['mailing.test.blacklist'].create({'email_from':'arya.stark@example.com'})
        record2=self.env['mailing.test.blacklist'].create({'email_from':'not.arya.stark@example.com'})

        search_res=self.env['mailing.test.blacklist'].search([('is_blacklisted','=',False)])
        self.assertEqual(search_res,record2)

        search_res=self.env['mailing.test.blacklist'].search([('is_blacklisted','!=',True)])
        self.assertEqual(search_res,record2)

        search_res=self.env['mailing.test.blacklist'].search([('is_blacklisted','=',True)])
        self.assertEqual(search_res,record1)

        search_res=self.env['mailing.test.blacklist'].search([('is_blacklisted','!=',False)])
        self.assertEqual(search_res,record1)

    @users('employee')
    deftest_bl_mixin_search_blacklisted_format(self):
        """Testis_blacklistedfieldsearchusingemailparsing"""
        record1=self.env['mailing.test.blacklist'].create({'email_from':'AryaStark<arya.stark@example.com>'})
        self.assertTrue(record1.is_blacklisted)

        search_res=self.env['mailing.test.blacklist'].search([('is_blacklisted','=',True)])
        self.assertEqual(search_res,record1)
