#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.testsimportcommon


classTestHrCommon(common.TransactionCase):

    defsetUp(self):
        super(TestHrCommon,self).setUp()

        self.res_users_hr_officer=mail_new_test_user(self.env,login='hro',groups='base.group_user,hr.group_hr_user',name='HROfficer',email='hro@example.com')
