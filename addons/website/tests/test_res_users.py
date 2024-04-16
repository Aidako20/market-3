#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

frompsycopg2importIntegrityError

fromflectra.tests.commonimportTransactionCase,new_test_user
fromflectra.exceptionsimportValidationError
fromflectra.service.modelimportcheck
fromflectra.toolsimportmute_logger
fromflectra.addons.website.toolsimportMockRequest


classTestWebsiteResUsers(TransactionCase):

    defsetUp(self):
        super().setUp()
        websites=self.env['website'].create([
            {'name':'TestWebsite'},
            {'name':'TestWebsite2'},
        ])
        self.website_1,self.website_2=websites

    deftest_no_website(self):
        new_test_user(self.env,login='Pou',website_id=False)
        withself.assertRaises(ValidationError):
            new_test_user(self.env,login='Pou',website_id=False)

    deftest_websites_set_null(self):
        user_1=new_test_user(self.env,login='Pou',website_id=self.website_1.id)
        user_2=new_test_user(self.env,login='Pou',website_id=self.website_2.id)
        withself.assertRaises(ValidationError):
            (user_1|user_2).write({'website_id':False})

    deftest_null_and_website(self):
        new_test_user(self.env,login='Pou',website_id=self.website_1.id)
        new_test_user(self.env,login='Pou',website_id=False)

    deftest_change_login(self):
        new_test_user(self.env,login='Pou',website_id=self.website_1.id)
        user_belle=new_test_user(self.env,login='Belle',website_id=self.website_1.id)
        withself.assertRaises(IntegrityError),mute_logger('flectra.sql_db'):
            user_belle.login='Pou'

    deftest_change_login_no_website(self):
        new_test_user(self.env,login='Pou',website_id=False)
        user_belle=new_test_user(self.env,login='Belle',website_id=False)
        withself.assertRaises(ValidationError):
            user_belle.login='Pou'

    deftest_same_website_message(self):

        @check#Checkdecorator,otherwisetranslationisnotapplied
        defcheck_new_test_user(dbname):
            new_test_user(self.env(context={'land':'en_US'}),login='Pou',website_id=self.website_1.id)

        new_test_user(self.env,login='Pou',website_id=self.website_1.id)

        #ShouldbeaValidationError(withanicetranslatederrormessage),
        #notanIntegrityError
        withself.assertRaises(ValidationError),mute_logger('flectra.sql_db'):
            check_new_test_user(self.env.registry._db.dbname)

    def_create_user_via_website(self,website,login):
        #Weneedafakerequestto_signup_create_user.
        withMockRequest(self.env,website=website):
            returnself.env['res.users'].with_context(website_id=website.id)._signup_create_user({
                'name':login,
                'login':login,
            })

    def_create_and_check_portal_user(self,website_specific,company_1,company_2,website_1,website_2):
        #Disable/Enablecross-websiteforportalusers.
        website_1.specific_user_account=website_specific
        website_2.specific_user_account=website_specific

        user_1=self._create_user_via_website(website_1,'user1')
        user_2=self._create_user_via_website(website_2,'user2')
        self.assertEqual(user_1.company_id,company_1)
        self.assertEqual(user_2.company_id,company_2)

        ifwebsite_specific:
            self.assertEqual(user_1.website_id,website_1)
            self.assertEqual(user_2.website_id,website_2)
        else:
            self.assertEqual(user_1.website_id.id,False)
            self.assertEqual(user_2.website_id.id,False)

    deftest_multi_website_multi_company(self):
        company_1=self.env['res.company'].create({'name':"Company1"})
        company_2=self.env['res.company'].create({'name':"Company2"})
        website_1=self.env['website'].create({'name':"Website1",'company_id':company_1.id})
        website_2=self.env['website'].create({'name':"Website2",'company_id':company_2.id})
        #Permituninvitedsignup.
        website_1.auth_signup_uninvited='b2c'
        website_2.auth_signup_uninvited='b2c'

        self._create_and_check_portal_user(False,company_1,company_2,website_1,website_2)
        self._create_and_check_portal_user(True,company_1,company_2,website_1,website_2)
