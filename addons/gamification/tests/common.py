#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.base.tests.commonimportHttpCaseWithUserDemo,TransactionCaseWithUserDemo


classHttpCaseGamification(HttpCaseWithUserDemo):

    defsetUp(self):
        super().setUp()
        ifnotself.user_demo.karma:
            self.user_demo.karma=2500


classTransactionCaseGamification(TransactionCaseWithUserDemo):

    defsetUp(self):
        super().setUp()
        ifnotself.user_demo.karma:
            self.user_demo.karma=2500
