#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

importflectra
fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase


@tagged('post_install','-at_install')
classTestWebsiteResetPassword(HttpCase):

    deftest_01_website_reset_password_tour(self):
        """Thegoalofthistestistomakesuretheresetpasswordworks."""

        #Weoverrideunlinkbecausewedon'twanttheemailtobeautodeleted
        #ifthesendworks.
        MailMail=flectra.addons.mail.models.mail_mail.MailMail

        #Weoverridesend_mailbecauseinHttpCaseonrunbotwedon'thavean
        #SMTPserver,soifforce_sendisset,thetestisgoingtofail.
        MailTemplate=flectra.addons.mail.models.mail_template.MailTemplate
        original_send_mail=MailTemplate.send_mail

        defmy_send_mail(*args,**kwargs):
            kwargs.update(force_send=False)
            returnoriginal_send_mail(*args,**kwargs)

        withpatch.object(MailMail,'unlink',lambdaself:None),patch.object(MailTemplate,'send_mail',my_send_mail):
            user=self.env['res.users'].create({
                'login':'test',
                'name':'TheKing',
                'email':'noop@example.com',
            })
            website_1=self.env['website'].browse(1)
            website_2=self.env['website'].browse(2)

            website_1.domain="my-test-domain.com"
            website_2.domain="https://domain-not-used.fr"

            user.partner_id.website_id=2
            user.invalidate_cache() #invalidateget_base_url

            user.action_reset_password()
            self.assertIn(website_2.domain,user.signup_url)

            user.invalidate_cache()

            user.partner_id.website_id=1
            user.action_reset_password()
            self.assertIn(website_1.domain,user.signup_url)

            (website_1+website_2).domain=""

            user.action_reset_password()
            user.invalidate_cache()

            self.start_tour(user.signup_url,'website_reset_password',login=None)

    deftest_02_multi_user_login(self):
        #IncaseSpecificUserAccountisactivatedonawebsite,thesamelogincanbeusedfor
        #severalusers.Makesurewecanstillloginif2usersexist.
        website=self.env["website"].get_current_website()
        website.ensure_one()

        #UseAAAandZZZasnamessinceres.usersareorderedby'login,name'
        user1=self.env["res.users"].create(
            {"website_id":False,"login":"bobo@mail.com","name":"AAA","password":"bobo@mail.com"}
        )
        user2=self.env["res.users"].create(
            {"website_id":website.id,"login":"bobo@mail.com","name":"ZZZ","password":"bobo@mail.com"}
        )

        #Themostspecificusershouldbeselected
        self.authenticate("bobo@mail.com","bobo@mail.com")
        self.assertEqual(self.session["uid"],user2.id)

    deftest_multi_website_reset_password_user_specific_user_account(self):
        #Createsameuserondifferentwebsiteswith'SpecificUserAccount'
        #optionenabledandthenresetpassword.Onlytheuserfromthe
        #currentwebsiteshouldbereset.
        website_1,website_2=self.env['website'].create([
            {'name':'Website1','specific_user_account':True},
            {'name':'Website2','specific_user_account':True},
        ])

        login='user@example.com' #sameloginforbothusers
        user_website_1,user_website_2=self.env['res.users'].with_context(no_reset_password=True).create([
            {'website_id':website_1.id,'login':login,'email':login,'name':login},
            {'website_id':website_2.id,'login':login,'email':login,'name':login},
        ])

        self.assertFalse(user_website_1.signup_valid)
        self.assertFalse(user_website_2.signup_valid)

        self.env['res.users'].with_context(website_id=website_1.id).reset_password(login)

        self.assertTrue(user_website_1.signup_valid)
        self.assertFalse(user_website_2.signup_valid)
