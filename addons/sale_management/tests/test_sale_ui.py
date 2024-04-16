importflectra.tests
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    deftest_01_sale_tour(self):
        self.start_tour("/web",'sale_tour',login="admin",step_delay=100)
