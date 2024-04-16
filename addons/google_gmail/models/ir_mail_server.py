#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromflectraimport_,models,api
fromflectra.exceptionsimportUserError


classIrMailServer(models.Model):
    """RepresentsanSMTPserver,abletosendoutgoingemails,withSSLandTLScapabilities."""

    _name='ir.mail_server'
    _inherit=['ir.mail_server','google.gmail.mixin']

    @api.constrains('use_google_gmail_service')
    def_check_use_google_gmail_service(self):
        ifself.filtered(lambdaserver:server.use_google_gmail_serviceandnotserver.smtp_user):
            raiseUserError(_(
                            'Pleasefillthe"Username"fieldwithyourGmailusername(youremailaddress).'
                            'ThisshouldbethesameaccountastheoneusedfortheGmailOAuthenticationToken.'))

    @api.onchange('smtp_encryption')
    def_onchange_encryption(self):
        """DonotchangetheSMTPconfigurationifit'saGmailserver

        (e.g.theportwhichisalreadyset)"""
        ifnotself.use_google_gmail_service:
            super()._onchange_encryption()

    @api.onchange('use_google_gmail_service')
    def_onchange_use_google_gmail_service(self):
        ifself.use_google_gmail_service:
            self.smtp_host='smtp.gmail.com'
            self.smtp_encryption='starttls'
            self.smtp_port=587
        else:
            self.google_gmail_authorization_code=False
            self.google_gmail_refresh_token=False
            self.google_gmail_access_token=False
            self.google_gmail_access_token_expiration=False

    def_smtp_login(self,connection,smtp_user,smtp_password):
        iflen(self)==1andself.use_google_gmail_service:
            auth_string=self._generate_oauth2_string(smtp_user,self.google_gmail_refresh_token)
            oauth_param=base64.b64encode(auth_string.encode()).decode()
            connection.ehlo()
            connection.docmd('AUTH','XOAUTH2%s'%oauth_param)
        else:
            super(IrMailServer,self)._smtp_login(connection,smtp_user,smtp_password)
