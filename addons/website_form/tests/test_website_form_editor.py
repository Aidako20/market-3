#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
#-*-coding:utf-8-*-

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestWebsiteFormEditor(flectra.tests.HttpCase):
    deftest_tour(self):
        self.start_tour("/",'website_form_editor_tour',login="admin")
        self.start_tour("/",'website_form_editor_tour_submit')
        self.start_tour("/",'website_form_editor_tour_results',login="admin")
