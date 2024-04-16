#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

importflectra
fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase


@tagged('post_install','-at_install')
classTestWebsiteSaleMail(HttpCase):

    deftest_01_shop_mail_tour(self):
        """ThegoalofthistestistomakesuresendingSObyemailworks."""

        self.env['product.product'].create({
            'name':'AcousticBlocScreens',
            'list_price':2950.0,
            'website_published':True,
        })
        self.env['res.partner'].create({
            'name':'AzureInterior',
            'email':'azure.Interior24@example.com',
        })

        #weoverrideunlinkbecausewedon'twanttheemailtobeautodeleted
        MailMail=flectra.addons.mail.models.mail_mail.MailMail

        withpatch.object(MailMail,'unlink',lambdaself:None):
            self.start_tour("/",'shop_mail',login="admin")
