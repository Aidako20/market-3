#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestIAP(TransactionCase):
    deftest_get_account(self):
        account=self.env["iap.account"].get("random_service_name")
        self.assertTrue(account.account_token,"Mustbeabletoreadthefield")
