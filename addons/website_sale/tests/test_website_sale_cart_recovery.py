#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimporttagged
fromflectra.tests.commonimportHttpCase,TransactionCase
fromflectra.addons.base.tests.commonimportHttpCaseWithUserPortal

@tagged('post_install','-at_install')
classTestWebsiteSaleCartRecovery(HttpCaseWithUserPortal):

    deftest_01_shop_cart_recovery_tour(self):
        """Thegoalofthistestistomakesurecartrecoveryworks."""
        self.env['product.product'].create({
            'name':'AcousticBlocScreens',
            'list_price':2950.0,
            'website_published':True,
        })

        self.start_tour("/",'shop_cart_recovery',login="portal")


@tagged('post_install','-at_install')
classTestWebsiteSaleCartRecoveryServer(TransactionCase):

    defsetUp(self):
        res=super(TestWebsiteSaleCartRecoveryServer,self).setUp()

        self.customer=self.env['res.partner'].create({
            'name':'a',
            'email':'a@example.com',
        })
        self.recovery_template_default=self.env.ref('website_sale.mail_template_sale_cart_recovery')
        self.recovery_template_custom1=self.recovery_template_default.copy()
        self.recovery_template_custom2=self.recovery_template_default.copy()

        self.website0=self.env['website'].create({
            'name':'web0',
            'cart_recovery_mail_template_id':self.recovery_template_default.id,
        })
        self.website1=self.env['website'].create({
            'name':'web1',
            'cart_recovery_mail_template_id':self.recovery_template_custom1.id,
        })
        self.website2=self.env['website'].create({
            'name':'web2',
            'cart_recovery_mail_template_id':self.recovery_template_custom2.id,
        })
        self.so0=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'website_id':self.website0.id,
            'is_abandoned_cart':True,
            'cart_recovery_email_sent':False,
        })
        self.so1=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'website_id':self.website1.id,
            'is_abandoned_cart':True,
            'cart_recovery_email_sent':False,
        })
        self.so2=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'website_id':self.website2.id,
            'is_abandoned_cart':True,
            'cart_recovery_email_sent':False,
        })

        returnres

    deftest_cart_recovery_mail_template(self):
        """Makesurethatwegetthecorrectcartrecoverytemplatestosend."""
        self.assertEqual(
            self.so1._get_cart_recovery_template(),
            self.recovery_template_custom1,
            "Wedonotreturnthecorrectmailtemplate"
        )
        self.assertEqual(
            self.so2._get_cart_recovery_template(),
            self.recovery_template_custom2,
            "Wedonotreturnthecorrectmailtemplate"
        )
        #Ordersthatbelongtodifferentwebsites;weshouldgetthedefaulttemplate
        self.assertEqual(
            (self.so1+self.so2)._get_cart_recovery_template(),
            self.recovery_template_default,
            "Wedonotreturnthecorrectmailtemplate"
        )

    deftest_cart_recovery_mail_template_send(self):
        """Thegoalofthistestistomakesurecartrecoveryworks."""
        orders=self.so0+self.so1+self.so2

        self.assertFalse(
            any(orders.mapped('cart_recovery_email_sent')),
            "Therecoverymailshouldnothavebeensentyet."
        )
        self.assertFalse(
            any(orders.mapped('access_token')),
            "Thereshouldnotbeanaccesstokenyet."
        )

        orders._cart_recovery_email_send()

        self.assertTrue(
            all(orders.mapped('cart_recovery_email_sent')),
            "Therecoverymailshouldhavebeensent."
        )
        self.assertTrue(
            all(orders.mapped('access_token')),
            "Alltokensshouldhavebeengenerated."
        )

        sent_mail={}
        fororderinorders:
            mail=self.env["mail.mail"].search([
                ('record_name','=',order['name'])
            ])
            sent_mail.update({order:mail})

        self.assertTrue(
            all(len(sent_mail[order])==1fororderinorders),
            "Eachcartrecoverymailhasbeensentexactlyonce."
        )
        self.assertTrue(
            all(order.access_tokeninsent_mail[order].bodyfororderinorders),
            "EachmailshouldcontaintheaccesstokenofthecorrespondingSO."
        )
