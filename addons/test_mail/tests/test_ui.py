#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    deftest_01_mail_tour(self):
        self.start_tour("/web",'mail_tour',login="admin")
