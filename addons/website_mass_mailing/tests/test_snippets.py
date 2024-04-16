#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra
importflectra.tests


@flectra.tests.common.tagged('post_install','-at_install')
classTestSnippets(flectra.tests.HttpCase):

    deftest_01_newsletter_popup(self):
        self.start_tour("/?enable_editor=1","newsletter_popup_edition",login='admin')
        self.start_tour("/","newsletter_popup_use",login=None)
        mailing_list=self.env['mailing.list'].search([],limit=1)
        emails=mailing_list.contact_ids.mapped('email')
        self.assertIn("hello@world.com",emails)
