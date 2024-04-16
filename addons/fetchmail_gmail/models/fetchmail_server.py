#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError


classFetchmailServer(models.Model):
    _name='fetchmail.server'
    _inherit=['fetchmail.server','google.gmail.mixin']

    @api.constrains('use_google_gmail_service','server_type')
    def_check_use_google_gmail_service(self):
        ifany(server.use_google_gmail_serviceandserver.server_type!='imap'forserverinself):
            raiseUserError(_('GmailauthenticationonlysupportsIMAPservertype.'))

    @api.onchange('use_google_gmail_service')
    def_onchange_use_google_gmail_service(self):
        """SetthedefaultconfigurationforaIMAPGmailserver."""
        ifself.use_google_gmail_service:
            self.server='imap.gmail.com'
            self.server_type='imap'
            self.is_ssl=True
            self.port=993
        else:
            self.google_gmail_authorization_code=False
            self.google_gmail_refresh_token=False
            self.google_gmail_access_token=False
            self.google_gmail_access_token_expiration=False

    def_imap_login(self,connection):
        """AuthenticatetheIMAPconnection.

        IfthemailserverisGmail,weusetheOAuth2authenticationprotocol.
        """
        self.ensure_one()
        ifself.use_google_gmail_service:
            auth_string=self._generate_oauth2_string(self.user,self.google_gmail_refresh_token)
            connection.authenticate('XOAUTH2',lambdax:auth_string)
            connection.select('INBOX')
        else:
            super(FetchmailServer,self)._imap_login(connection)
