#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.exceptionsimportUserError
fromflectra.testsimporttagged
fromflectra.tests.commonimportBaseCase


@tagged('phone_validation')
classTestPhonenumbers(BaseCase):

    deftest_country_code_falsy(self):
        self.assertEqual(
            phone_validation.phone_format('0456998877','BE','32',force_format='E164'),
            '+32456998877'
        )
        #nocountrycode->UserError,nointernaltraceback
        withself.assertRaises(UserError):
            self.assertEqual(
                phone_validation.phone_format('0456998877',None,'32',force_format='E164'),
                '+32456998877'
            )
