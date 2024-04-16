#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mass_mailing.tests.commonimportTestMassMailCommon
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger


classTestMailingTest(TestMassMailCommon):

    @users('user_marketing')
    @mute_logger('flectra.addons.mail.models.mail_render_mixin')
    deftest_mailing_test_button(self):
        mailing=self.env['mailing.mailing'].create({
            'name':'TestButton',
            'subject':'Subject${object.name}',
            'preview':'Preview${object.name}',
            'state':'draft',
            'mailing_type':'mail',
            'body_html':'<p>Hello${object.name}</p>',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
        })
        mailing_test=self.env['mailing.mailing.test'].create({
            'email_to':'test@test.com',
            'mass_mailing_id':mailing.id,
        })

        withself.mock_mail_gateway():
            mailing_test.send_mail_test()

        #Testifbadjinjainthesubjectraisesanerror
        mailing.write({'subject':'Subject${object.name_id.id}'})
        withself.mock_mail_gateway(),self.assertRaises(Exception):
            mailing_test.send_mail_test()

        #Testifbadjinjainthebodyraisesanerror
        mailing.write({
            'subject':'Subject${object.name}',
            'body_html':'<p>Hello${object.name_id.id}</p>',
        })
        withself.mock_mail_gateway(),self.assertRaises(Exception):
            mailing_test.send_mail_test()

        #Testifbadjinjainthepreviewraisesanerror
        mailing.write({
            'body_html':'<p>Hello${object.name}</p>',
            'preview':'Preview${object.name_id.id}',
        })
        withself.mock_mail_gateway(),self.assertRaises(Exception):
            mailing_test.send_mail_test()
