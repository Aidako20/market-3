#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon,tagged


@tagged('-at_install','post_install')
classTestAuthSignupUninvited(common.TransactionCase):

    deftest_01_auth_signup_uninvited(self):
        self.env['website'].browse(1).auth_signup_uninvited='b2c'
        config=self.env['res.config.settings'].create({})
        self.assertEqual(config.auth_signup_uninvited,'b2c')
