#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.testsimporttagged,users


@tagged('mail_tools')
classTestMailTools(TestMailCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestMailTools,cls).setUpClass()

        cls._test_email='alfredoastaire@test.example.com'
        cls.test_partner=cls.env['res.partner'].create({
            'country_id':cls.env.ref('base.be').id,
            'email':cls._test_email,
            'mobile':'0456001122',
            'name':'AlfredAstaire',
            'phone':'0456334455',
        })

    @users('employee')
    deftest_mail_find_partner_from_emails(self):
        Partner=self.env['res.partner']
        test_partner=Partner.browse(self.test_partner.ids)
        self.assertEqual(test_partner.email,self._test_email)

        sources=[
            self._test_email, #testdirectmatch
            f'"NorbertPoiluchette"<{self._test_email}>', #encapsulated
            'fredoastaire@test.example.com', #partialemail->shouldnotmatch!
        ]
        expected_partners=[
            test_partner,
            test_partner,
            self.env['res.partner'],
        ]
        forsource,expected_partnerinzip(sources,expected_partners):
            withself.subTest(source=source):
                found=Partner._mail_find_partner_from_emails([source])
                self.assertEqual(found,[expected_partner])

        #testwithwildcard"_"
        found=Partner._mail_find_partner_from_emails(['alfred_astaire@test.example.com'])
        self.assertEqual(found,[self.env['res.partner']])
        #sub-check:thissearchdoesnotconsider_asawildcard
        found=Partner._mail_search_on_partner(['alfred_astaire@test.example.com'])
        self.assertEqual(found,self.env['res.partner'])

        #testpartnerswithencapsulatedemails
        #------------------------------------------------------------
        test_partner.sudo().write({'email':f'"AlfredMightyPowerAstaire"<{self._test_email}>'})

        sources=[
            self._test_email, #testdirectmatch
            f'"NorbertPoiluchette"<{self._test_email}>', #encapsulated
        ]
        expected_partners=[
            test_partner,
            test_partner,
        ]
        forsource,expected_partnerinzip(sources,expected_partners):
            withself.subTest(source=source):
                found=Partner._mail_find_partner_from_emails([source])
                self.assertEqual(found,[expected_partner])

        #testwithwildcard"_"
        found=Partner._mail_find_partner_from_emails(['alfred_astaire@test.example.com'])
        self.assertEqual(found,[self.env['res.partner']])
        #sub-check:thissearchdoesnotconsider_asawildcard
        found=Partner._mail_search_on_partner(['alfred_astaire@test.example.com'])
        self.assertEqual(found,self.env['res.partner'])

    @users('employee')
    deftest_mail_find_partner_from_emails_followers(self):
        """Test'_mail_find_partner_from_emails'whendealingwithrecordson
        whichfollowershavetobefoundbasedonemail.Checkmultiemail
        andencapsulatedemailsupport."""
        linked_record=self.env['mail.test.simple'].create({'name':'Recordforfollowers'})
        follower_partner=self.env['res.partner'].sudo().create({
            'email':self._test_email,
            'name':'Duplicated,followerofrecord',
        })
        linked_record.message_subscribe(partner_ids=follower_partner.ids)
        test_partner=self.test_partner.with_env(self.env)

        #standardtest,nomulti-email,toassertbasebehavior
        sources=[(self._test_email,True),(self._test_email,False),]
        expected=[follower_partner,test_partner]
        for(source,follower_check),expectedinzip(sources,expected):
            withself.subTest(source=source,follower_check=follower_check):
                partner=self.env['res.partner']._mail_find_partner_from_emails(
                    [source],records=linked_recordiffollower_checkelseNone
                )[0]
                self.assertEqual(partner,expected)

        #formattedemail
        encapsulated_test_email=f'"RobertAstaire"<{self._test_email}>'
        (follower_partner+test_partner).sudo().write({'email':encapsulated_test_email})
        sources=[
            (self._test_email,True), #normalized
            (self._test_email,False), #normalized
            (encapsulated_test_email,True), #encapsulated,same
            (encapsulated_test_email,False), #encapsulated,same
            (f'"AnotherName"<{self._test_email}',True), #samenormalized,othername
            (f'"AnotherName"<{self._test_email}',False), #samenormalized,othername
        ]
        expected=[follower_partner,test_partner,
                    follower_partner,test_partner,
                    follower_partner,test_partner,
                    follower_partner,test_partner]
        for(source,follower_check),expectedinzip(sources,expected):
            withself.subTest(source=source,follower_check=follower_check):
                partner=self.env['res.partner']._mail_find_partner_from_emails(
                    [source],records=linked_recordiffollower_checkelseNone
                )[0]
                self.assertEqual(partner,expected,
                                'Mail:formattedemailisrecognizedthroughusageofnormalizedemail')

        #multi-email
        _test_email_2='"RobertAstaire"<not.alfredoastaire@test.example.com>'
        (follower_partner+test_partner).sudo().write({'email':f'{self._test_email},{_test_email_2}'})
        sources=[
            (self._test_email,True), #firstemail
            (self._test_email,False), #firstemail
            (_test_email_2,True), #secondemail
            (_test_email_2,False), #secondemail
            ('not.alfredoastaire@test.example.com',True), #normalizedsecondemailinfield
            ('not.alfredoastaire@test.example.com',False), #normalizedsecondemailinfield
            (f'{self._test_email},{_test_email_2}',True), #multi-email,bothmatching,dependsoncomparison
            (f'{self._test_email},{_test_email_2}',False) #multi-email,bothmatching,dependsoncomparison
        ]
        expected=[follower_partner,test_partner,
                    self.env['res.partner'],self.env['res.partner'],
                    self.env['res.partner'],self.env['res.partner'],
                    follower_partner,test_partner]
        for(source,follower_check),expectedinzip(sources,expected):
            withself.subTest(source=source,follower_check=follower_check):
                partner=self.env['res.partner']._mail_find_partner_from_emails(
                    [source],records=linked_recordiffollower_checkelseNone
                )[0]
                self.assertEqual(partner,expected,
                                'Mail(FIXME):partialrecognitionofmultiemailthroughemail_normalize')
