#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportexceptions,tools
fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.tests.commonimporttagged
fromflectra.toolsimportmute_logger


@tagged('mail_thread','mail_blacklist')
classTestMailThread(TestMailCommon,TestRecipients):

    @mute_logger('flectra.models.unlink')
    deftest_blacklist_mixin_email_normalized(self):
        """Testemail_normalizedandis_blacklistedfieldsbehavior,notably
        whendealingwithencapsulatedemailfieldsandmulti-emailinput."""
        base_email='test.email@test.example.com'

        #testdata:sourceemail,expectedemailnormalized
        valid_pairs=[
            (base_email,base_email),
            (tools.formataddr(('AnotherName',base_email)),base_email),
            (f'NameThatShouldBeEscaped<{base_email}>',base_email),
            ('test.😊@example.com','test.😊@example.com'),
            ('"Name😊"<test.😊@example.com>','test.😊@example.com'),
        ]
        void_pairs=[(False,False),
                      ('',False),
                      ('',False)]
        multi_pairs=[
            (f'{base_email},other.email@test.example.com',
             base_email), #multisupportsfirstfound
            (f'{tools.formataddr(("AnotherName",base_email))},other.email@test.example.com',
             base_email), #multisupportsfirstfound
        ]
        foremail_from,exp_email_normalizedinvalid_pairs+void_pairs+multi_pairs:
            withself.subTest(email_from=email_from,exp_email_normalized=exp_email_normalized):
                new_record=self.env['mail.test.gateway'].create({
                    'email_from':email_from,
                    'name':'BLTest',
                })
                self.assertEqual(new_record.email_normalized,exp_email_normalized)
                self.assertFalse(new_record.is_blacklisted)

                #blacklistemailshouldfailasvoid
                ifemail_fromin[pair[0]forpairinvoid_pairs]:
                    withself.assertRaises(exceptions.UserError):
                        bl_record=self.env['mail.blacklist']._add(email_from)
                #blacklistemailcurrentlyfailsbutcouldnot
                elifemail_fromin[pair[0]forpairinmulti_pairs]:
                    withself.assertRaises(exceptions.UserError):
                        bl_record=self.env['mail.blacklist']._add(email_from)
                #blacklistemailok
                else:
                    bl_record=self.env['mail.blacklist']._add(email_from)
                    self.assertEqual(bl_record.email,exp_email_normalized)
                    new_record.invalidate_cache(fnames=['is_blacklisted'])
                    self.assertTrue(new_record.is_blacklisted)

                bl_record.unlink()
