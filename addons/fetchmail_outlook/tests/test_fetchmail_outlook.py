#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime

fromunittest.mockimportANY,Mock,patch

fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportSavepointCase


classTestFetchmailOutlook(SavepointCase):

    @patch('flectra.addons.fetchmail.models.fetchmail.IMAP4_SSL')
    deftest_connect(self,mock_imap):
        """Testthattheconnectmethodwillusetheright
        authenticationmethodwiththerightarguments.
        """
        mock_connection=Mock()
        mock_imap.return_value=mock_connection

        mail_server=self.env['fetchmail.server'].create({
            'name':'Testserver',
            'use_microsoft_outlook_service':True,
            'user':'test@example.com',
            'microsoft_outlook_access_token':'test_access_token',
            'microsoft_outlook_access_token_expiration':time.time()+1000000,
            'password':'',
            'server_type':'imap',
            'is_ssl':True,
        })

        mail_server.connect()

        mock_connection.authenticate.assert_called_once_with('XOAUTH2',ANY)
        args=mock_connection.authenticate.call_args[0]

        self.assertEqual(args[1](None),'user=test@example.com\1auth=Bearertest_access_token\1\1',
                         msg='Shouldusetherightaccesstoken')

        mock_connection.select.assert_called_once_with('INBOX')

    deftest_constraints(self):
        """TesttheconstraintsrelatedtotheOutlookmailserver."""
        withself.assertRaises(UserError,msg='Shouldensurethatthepasswordisempty'):
            self.env['fetchmail.server'].create({
                'name':'Testserver',
                'use_microsoft_outlook_service':True,
                'password':'test',
                'server_type':'imap',
            })

        withself.assertRaises(UserError,msg='ShouldensurethattheservertypeisIMAP'):
            self.env['fetchmail.server'].create({
                'name':'Testserver',
                'use_microsoft_outlook_service':True,
                'password':'',
                'server_type':'pop',
            })
